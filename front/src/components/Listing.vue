<template>
  <div>
    <h3>Liste d'appartements</h3>
    <v-row>
      <!-- Colonne 1 : Tableau des appartements -->
      <v-col cols="12" md="8">
        <v-data-table :headers="headers" :items="suites" class="elevation-1">
          <template v-slot:item.accommodates="{ item }">
            <span>{{ item.accommodates }}</span>
          </template>
          <template v-slot:item.log_price="{ item }">
            <span>{{ Math.round(Math.exp(item.log_price), 2) }} €</span>
          </template>
          <template v-slot:item.city="{ item }">
            <span>{{ item.city }}</span>
          </template>
          <template v-slot:item.cleaning_fee="{ item }">
            <span>{{ item.cleaning_fee === "True" ? "Oui" : "Non" }}</span>
          </template>
          <template v-slot:item.c="{ item }">
            <span>{{ item.instant_bookable === t ? "Oui" : "Non" }}</span>
          </template>
        </v-data-table>
      </v-col>

      <v-col cols="12" md="4">
        <add @appartement-ajoute="ajouterAppartement" />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { defineComponent, reactive, onMounted } from "vue";
import Add from "./Add.vue";
import axios from "axios";

export default defineComponent({
  components: {
    Add,
  },
  setup() {
    const headers = [
      { title: "Nombre de personnes", key: "accommodates", align: "center" },
      { title: "Prix", key: "log_price", align: "center" },
      { title: "Ville", key: "city", align: "center" },
      { title: "Frais de ménage", key: "cleaning_fee", align: "center" },
      {
        title: "Réservable instantanément",
        key: "instant_bookable",
        align: "center",
      },
    ];

    let suites = reactive([]);

    // Fonction pour charger les appartements depuis l'API
    const fetchAppartements = async () => {
      try {
        const response = await axios.get(
          "http://localhost:3000/api/appartements"
        );
        suites.push(...response.data); // Charger les données de l'API dans suites
      } catch (error) {
        console.error("Erreur lors du chargement des appartements :", error);
      }
    };

    // Charger les appartements au montage du composant
    onMounted(fetchAppartements);

    const ajouterAppartement = async (nouvelAppartement) => {
      // Envoyer l'appartement au serveur avec Axios
      const response = await axios.post(
        "http://localhost:3000/api/appartements",
        { id: suites.length + 1, ...nouvelAppartement }
      );
      console.log("response", response);

      suites = response.data;
    };

    return { headers, suites, ajouterAppartement };
  },
});
</script>
