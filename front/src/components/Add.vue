<template>
  <div>
    <v-card class="mx-auto" max-width="600">
      <v-card-title>
        <h3>Nouvel appartement</h3>
      </v-card-title>
      <v-card-text>
        <form @submit.prevent="ajouterAppartement">
          <div>
            <v-text-field
              label="Nombre de personnes"
              v-model="nouvelAppartement.accommodates"
              type="number"
              id="accommodates"
              required
            />
          </div>
          <div>
            <label for="city">Ville :</label>
            <v-text-field v-model="nouvelAppartement.city" id="city" required />
          </div>
          <div>
            <label for="nbWindows">A des frais de ménage :</label>
            <v-checkbox
              v-model="nouvelAppartement.cleaning_fee"
              id="cleaning_fee"
              required
            />
          </div>
          <div>
            <label for="price">Réservable instantanément :</label>
            <v-checkbox
              v-model="nouvelAppartement.instant_bookable"
              id="instant_bookable"
              required
            />
          </div>
          <div>
            <v-text-field
              label="Prix"
              v-model="nouvelAppartement.price"
              type="number"
              id="price"
              required
            />
          </div>
          <div v-if="prixConseille !== null">
            <p>Prix conseillé : {{ Math.round(prixConseille, 2) }}€</p>
          </div>
          <v-btn type="submit">Ajouter l'appartement</v-btn>
        </form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { defineComponent, reactive, ref, watch } from "vue";
import axios from "axios";

export default defineComponent({
  name: "AjoutAppartement",
  emits: ["appartement-ajoute"],
  setup(props, { emit }) {
    const nouvelAppartement = reactive({
      accommodates: null,
      city: "",
      cleaning_fee: false,
      instant_bookable: false,
    });

    const prixConseille = ref(null);
    const cities = ["NYC", "LA", "DC", "Boston", "SF", "Chicago"];

    const fetchPrixConseille = async () => {
      if (
        nouvelAppartement.accommodates &&
        cities.includes(nouvelAppartement.city) &&
        nouvelAppartement.cleaning_fee !== null &&
        nouvelAppartement.instant_bookable !== null
      ) {
        try {
          const response = await axios.post(
            "http://localhost:3000/api/predict",
            {
              accommodates: nouvelAppartement.accommodates,
              city: nouvelAppartement.city,
              cleaning_fee: nouvelAppartement.cleaning_fee,
              instant_bookable: nouvelAppartement.instant_bookable,
            }
          );

          prixConseille.value = response.data.suggested_price;
        } catch (error) {
          console.error("Erreur lors de la requête :", error);
        }
      }
    };

    watch(
      () => [
        nouvelAppartement.accommodates,
        nouvelAppartement.city,
        nouvelAppartement.cleaning_fee,
        nouvelAppartement.instant_bookable,
      ],
      fetchPrixConseille,
      { deep: true }
    );

    const ajouterAppartement = () => {
      // Générer un ID unique pour le nouvel appartement
      const nouvelId = Date.now();
      const appartementComplet = { ...nouvelAppartement, id: nouvelId };
      emit("appartement-ajoute", appartementComplet);

      // Réinitialiser le formulaire
      nouvelAppartement.accommodates = null;
      nouvelAppartement.city = "";
      nouvelAppartement.cleaning_fee = false;
      nouvelAppartement.instant_bookable = false;
      nouvelAppartement.price = null;
    };

    return { nouvelAppartement, ajouterAppartement, prixConseille };
  },
});
</script>
