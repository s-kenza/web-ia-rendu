const express = require("express");
const bodyParser = require("body-parser");
const fs = require("fs");
const csv = require("csv-parser");
const axios = require("axios");

const app = express();
const PORT = 3000;
const cors = require("cors");

app.use(cors());
app.use(bodyParser.json());

// Route pour récupérer la liste des appartements
app.get("/api/appartements", async (req, res) => {
  const results = [];
  let count = 0;

  fs.createReadStream("./data/data.csv")
    .pipe(csv())
    .on("data", (data) => {
      if (count < 1000) {
        results.push(data);
      }
      count++;
    })
    .on("end", () => {
      // Retourner les résultats en JSON
      res.json(results);
    })
    .on("error", (err) => {
      res.status(500).json({
        message: "Erreur lors de la lecture du fichier CSV",
        error: err,
      });
    });
});

// Route pour ajouter un nouvel appartement
app.post("/api/appartements", async (req, res) => {
  const newAppartement = req.body;

  // Lire les appartements existants
  const appartements = readAppartementsFromFile();

  // Ajouter l'ID unique (basé sur la date actuelle)
  newAppartement.id = Date.now();

  // Ajouter le nouvel appartement à la liste
  appartements.push(newAppartement);

  // Écrire la nouvelle liste dans le fichier JSON
  await writeAppartementsToFile(appartements);

  // Retourner l'appartement ajouté avec l'ID
  res.status(201).json(appartements);
});

app.post("/api/predict", async (req, res) => {
  const { accommodates, cleaning_fee, instant_bookable, city } = req.body;

  try {
    // Envoyer la requête à l'API de prédiction
    const response = await axios.post("http://localhost:5000/predict-price", {
      accommodates,
      cleaning_fee,
      instant_bookable,
      city,
    });

    // Retourner la réponse de l'API de prédiction
    res.json({
      success: true,
      suggested_price: response.data.predicted_price, // Assurez-vous que 'suggested_price' est la bonne clé dans la réponse
    });
  } catch (error) {
    console.error("Erreur lors de la requête de prédiction:", error);
    res.status(500).json({
      success: false,
      message: "Erreur lors de la récupération de la prédiction",
    });
  }
});

// Démarrer le serveur
app.listen(PORT, () => {
  console.log(`Serveur en écoute sur http://localhost:${PORT}`);
});
