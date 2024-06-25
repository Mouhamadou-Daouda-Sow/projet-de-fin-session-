# Projet de Réservation de Billets

Ce projet est une application web de réservation de billets pour des événements. Il est construit avec Flask, une micro-framework en Python, et utilise MySQL pour la base de données.

## Fonctionnalités

- Inscription et connexion des utilisateurs
- Affichage des événements disponibles
- Recherche et filtrage des événements
- Réservation de billets pour les événements
- Section d'administration pour gérer les événements (ajout, modification, suppression)

## Installation

### Configurez la base de données MySQL :
    - Créez une base de données MySQL.
    - Mettez à jour les informations de connexion dans le fichier `config.py`.


## Utilisation

### Page d'accueil

La page d'accueil affiche les événements disponibles. Les utilisateurs peuvent utiliser la barre de recherche pour filtrer les événements par nom, date, lieu et nombre de billets disponibles.

### Inscription et Connexion

Les utilisateurs peuvent s'inscrire et se connecter pour réserver des billets. Une fois connectés, ils peuvent voir leurs réservations.

### Réservation

Les utilisateurs connectés peuvent réserver des billets pour les événements disponibles. La page de réservation affiche les détails de l'événement et permet de confirmer la réservation.

### Section d'administration

Les utilisateurs avec des droits d'administrateur peuvent accéder à la section d'administration. Ils peuvent ajouter, modifier et supprimer des événements.

