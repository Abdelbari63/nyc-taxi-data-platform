# Journal de bord — Phase 1 : Databricks Bronze Ingestion

**Projet :** NYC Taxi Data Platform — End-to-End Data Engineering  
**Technologie principale :** Databricks, Apache Spark (PySpark), Delta Lake, Unity Catalog  
**Statut :** Terminée  
**Période :** Octobre 2026

## 1. Objectif de la phase

L'objectif de cette phase était d'intégrer les données historiques NYC Yellow Taxi dans Databricks, de vérifier leur intégrité après ingestion et de les stocker dans une table Bronze au format Delta Lake.

Cette étape constitue la première couche de la plateforme Data Engineering. Elle permet de disposer d'une source de données centralisée, traçable et réutilisable pour les traitements ultérieurs.

## 2. Source de données

Nous avons utilisé trois fichiers Parquet contenant les trajets de taxis jaunes de New York pour janvier, février et mars 2016.

| Fichier | Nombre de lignes |
|---|---:|
| `yellow_tripdata_2016-01.parquet` | 10 905 067 |
| `yellow_tripdata_2016-02.parquet` | 11 375 412 |
| `yellow_tripdata_2016-03.parquet` | 12 203 824 |
| **Total** | **34 484 303** |

Les trois fichiers partagent le même schéma source de 19 colonnes.

## 3. Configuration de Databricks

Les ressources suivantes ont été créées dans Unity Catalog :

- **Catalog :** `main`
- **Schema :** `nyc-taxi`
- **Volume :** `nyc_taxi_data`
- **Notebook :** `01_bronze_ingestion`

Les trois fichiers Parquet ont été déposés dans le volume Databricks, à l'emplacement :

`/Volumes/main/nyc-taxi/nyc_taxi_data/`

Cette configuration permet au notebook de lire les fichiers sans dépendre du chemin local de l'ordinateur.

## 4. Ingestion avec PySpark

Le notebook réalise les opérations suivantes :

1. Lecture des trois fichiers Parquet avec `spark.read.parquet()`.
2. Ajout de la colonne `source_file` pour identifier le fichier d'origine de chaque ligne.
3. Fusion des DataFrames avec `unionByName()`.
4. Ajout des métadonnées d'ingestion.
5. Génération d'un identifiant technique provisoire `event_id`.
6. Écriture des données au format Delta Lake dans Unity Catalog.

Les colonnes techniques ajoutées sont :

| Colonne | Utilité |
|---|---|
| `source_file` | Identifier le fichier source |
| `ingestion_run_id` | Identifier le lot d'ingestion |
| `ingested_at` | Enregistrer l'horodatage d'ingestion |
| `schema_version` | Versionner le schéma utilisé |
| `event_id` | Empreinte calculée à partir du contenu de la ligne et du fichier source |

La table créée est :

`main.\`nyc-taxi\`.bronze_taxi_trips`

**Remarque sur `event_id` :** il s'agit actuellement d'une empreinte de contenu, pas d'un identifiant unique garanti pour chaque ligne physique. Deux lignes identiques dans le même fichier peuvent avoir la même empreinte. Il ne faut donc pas l'utiliser comme preuve d'unicité avant d'avoir défini et testé une stratégie d'identification adaptée.

## 5. Vérification de l'ingestion

Après l'écriture, nous avons relu la table Delta depuis Unity Catalog et vérifié son nombre de lignes et son schéma.

| Contrôle | Résultat |
|---|---|
| Nombre total de lignes | 34 484 303 |
| Nombre de colonnes | 24 |
| Nombre de fichiers sources | 3 |
| Cohérence des comptes par fichier | Conforme |
| Identifiants `event_id` nuls | 0 |
| Métadonnées `source_file` nulles | 0 |
| Métadonnées `ingestion_run_id` nulles | 0 |
| Métadonnées `ingested_at` nulles | 0 |

Les comptes par fichier correspondent exactement aux résultats du profilage local de la Phase 0. L'ingestion a donc conservé le volume attendu des données.

## 6. Première analyse de qualité

Avant de préparer la couche Silver, nous avons évalué quelques règles de qualité sur la table Bronze.

| Règle | Nombre de lignes concernées |
|---|---:|
| Durée invalide : dépôt avant ou à l'heure de prise en charge | 35 981 |
| Nombre de passagers invalide : valeur inférieure ou égale à zéro | 1 638 |
| Distance négative | 0 |
| Horodatages manquants | 0 |

Ces catégories peuvent se chevaucher. Il ne faut donc pas additionner directement leurs effectifs pour obtenir le nombre total de lignes invalides.

## 7. Préparation de la séparation valide / invalide

Nous avons appliqué les règles de qualité pour séparer les données en deux ensembles :

- Les trajets respectant les règles définies.
- Les trajets ne respectant pas au moins une règle, conservés pour investigation.

| Ensemble | Nombre de lignes |
|---|---:|
| Bronze | 34 484 303 |
| Trajets valides selon les règles actuelles | 34 446 756 |
| Trajets invalides mis en quarantaine | 37 547 |

La somme des deux ensembles correspond au total Bronze. Les tables créées sont :

- `main.\`nyc-taxi\`.silver_taxi_trips`
- `main.\`nyc-taxi\`.quarantine_taxi_trips`

La table Silver contient actuellement les lignes qui passent les règles de validation définies. La table de quarantaine conserve les lignes rejetées et ajoute des informations sur les motifs de rejet.

**Limite actuelle :** la couche Silver n'est pas encore entièrement transformée. Les colonnes métier n'ont pas encore été standardisées et les attributs dérivés, les contrôles financiers, la politique de déduplication et les tests spécifiques à Silver restent à mettre en œuvre.

## 8. Compétences travaillées

Cette phase a permis de pratiquer :

- L'organisation des ressources avec Unity Catalog.
- La lecture de fichiers Parquet dans Databricks.
- La manipulation de DataFrames PySpark.
- La fusion de plusieurs sources avec `unionByName()`.
- L'ajout de métadonnées de traçabilité.
- La création de tables Delta Lake.
- La validation des volumes et des schémas.
- La mise en œuvre de règles de qualité.
- La séparation des données valides et des données en quarantaine.

## 9. Conclusion

La Phase 1 a permis de construire la première couche de données de la plateforme. Les trois fichiers historiques ont été ingérés dans Databricks, réunis dans une table Bronze et contrôlés par rapport aux volumes attendus. Les premières règles de qualité ont également permis d'identifier les trajets à conserver pour le traitement Silver et ceux à mettre en quarantaine.

La prochaine étape consiste à développer une véritable couche Silver : standardisation du schéma, nettoyage documenté, création de colonnes dérivées, contrôles métier, stratégie de déduplication et tests automatisés.
