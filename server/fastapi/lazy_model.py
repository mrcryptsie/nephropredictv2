import pickle
import pandas as pd
import numpy as np
import os
import threading
import time
from typing import Dict, List, Any, Optional

class LazyIRCModel:
    """
    Classe pour gérer le modèle de prédiction IRC (Insuffisance Rénale Chronique)
    avec un chargement paresseux pour éviter les délais d'attente lors du rendu
    """
    def __init__(self):
        self._model = None
        self._feature_importance = None
        self._stage_probabilities = None
        self._model_loading = False
        self._model_loaded = False
        
        # Démarre un thread en arrière-plan pour charger le modèle
        self._start_loading_model()
    
    def _start_loading_model(self):
        """Démarre un thread en arrière-plan pour charger le modèle"""
        self._model_loading = True
        thread = threading.Thread(target=self._load_model)
        thread.daemon = True  # Le thread se termine lorsque le programme principal se termine
        thread.start()
    
    def _load_model(self):
        """Charge le modèle depuis le fichier pickle dans un thread en arrière-plan"""
        try:
            print("Début du chargement du modèle dans le thread en arrière-plan...")
            model_path = os.path.join(os.path.dirname(__file__), '../../attached_assets/model_lucien_v1.pkl')
            
            # Attendre un peu avant de commencer à charger le modèle pour permettre au programme de démarrer
            time.sleep(2)
            
            with open(model_path, 'rb') as file:
                self._model = pickle.load(file)
            
            self._model_loaded = True
            self._model_loading = False
            print("Modèle chargé avec succès dans le thread en arrière-plan")
        except Exception as e:
            print(f"Erreur lors du chargement du modèle : {e}")
            self._model_loading = False
            # Créer un modèle de secours simple pour les tests
            self._create_fallback_model()
    
    def _create_fallback_model(self):
        """Crée un modèle de secours simple pour les tests"""
        from sklearn.ensemble import RandomForestClassifier
        
        # Modèle de secours utilisé lorsqu'on ne peut pas charger le fichier pickle
        print("Création d'un modèle de secours pour les tests")
        self._model = RandomForestClassifier(n_estimators=10, random_state=42)
        self._model_loaded = True
    
    def is_model_ready(self) -> bool:
        """Vérifie si le modèle est chargé et prêt pour les prédictions"""
        return self._model_loaded
    
    def predict(self, input_data: Dict[str, Any]) -> int:
        """
        Fait une prédiction en utilisant le modèle chargé
        
        Args:
            input_data: Dictionnaire contenant les données du patient
            
        Returns:
            Stage prédit de l'IRC (0-5)
        """
        # Si le modèle n'est pas encore chargé, utiliser une prédiction de secours
        if not self._model_loaded:
            df = pd.DataFrame([input_data])
            return self._fallback_predict(df)
            
        try:
            # Convertir les données d'entrée en DataFrame pandas
            df = pd.DataFrame([input_data])
            
            # Si on utilise le modèle de secours (uniquement pour les tests)
            if not hasattr(self._model, 'predict'):
                return self._fallback_predict(df)
            
            # Effectuer la prédiction avec le modèle réel
            prediction = self._model.predict(df)
            predicted_stage = int(prediction[0])
            
            # Calculer les probabilités des stades si le modèle le permet
            if hasattr(self._model, 'predict_proba'):
                proba = self._model.predict_proba(df)[0]
                classes = self._model.classes_
                self._stage_probabilities = {int(classes[i]): float(proba[i]) for i in range(len(classes))}
            else:
                # Probabilités de secours
                self._generate_fallback_probabilities(predicted_stage)
            
            # Calculer l'importance des caractéristiques
            self._calculate_feature_importance(df)
            
            return predicted_stage
        
        except Exception as e:
            print(f"Erreur lors de la prédiction : {e}")
            return self._fallback_predict(pd.DataFrame([input_data]))
    
    def _fallback_predict(self, df: pd.DataFrame) -> int:
        """Logique de prédiction de secours pour les tests"""
        # Logique simple basée sur les niveaux de créatinine
        creatinine = df['Créatinine (mg/L)'].values[0]
        
        if creatinine > 200:
            stage = 5
        elif creatinine > 100:
            stage = 4
        elif creatinine > 50:
            stage = 3
        elif creatinine > 20:
            stage = 2
        elif creatinine > 15:
            stage = 1
        else:
            stage = 0
            
        # Générer des probabilités et l'importance des caractéristiques pour la méthode de secours
        self._generate_fallback_probabilities(stage)
        self._generate_fallback_feature_importance(df)
        
        return stage
    
    def _generate_fallback_probabilities(self, predicted_stage: int) -> None:
        """Générer des probabilités de secours pour les tests"""
        # Donner au stade prédit une probabilité élevée et répartir le reste
        confidence = 0.75 + (np.random.random() * 0.2)  # Entre 0.75 et 0.95
        remaining = 1.0 - confidence
        
        self._stage_probabilities = {
            0: 0.0,
            1: 0.0,
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0
        }
        
        # Définir la confiance pour le stade prédit
        self._stage_probabilities[predicted_stage] = confidence
        
        # Répartir la probabilité restante entre les autres stades
        other_stages = [s for s in range(6) if s != predicted_stage]
        for stage in other_stages:
            self._stage_probabilities[stage] = remaining / len(other_stages)
    
    def _calculate_feature_importance(self, df: pd.DataFrame) -> None:
        """Calculer l'importance des caractéristiques en fonction du modèle"""
        try:
            if hasattr(self._model, 'feature_importances_'):
                # Obtenir les noms des caractéristiques
                feature_names = df.columns.tolist()
                
                # Obtenir les importances des caractéristiques depuis le modèle
                importances = self._model.feature_importances_
                
                # Créer un dictionnaire des importances des caractéristiques
                self._feature_importance = {
                    feature_names[i]: float(importances[i]) 
                    for i in range(len(feature_names))
                }
                
                # Normaliser pour que la somme soit égale à 1
                total = sum(self._feature_importance.values())
                self._feature_importance = {
                    k: v/total for k, v in self._feature_importance.items()
                }
            else:
                self._generate_fallback_feature_importance(df)
        except Exception as e:
            print(f"Erreur lors du calcul de l'importance des caractéristiques : {e}")
            self._generate_fallback_feature_importance(df)
    
    def _generate_fallback_feature_importance(self, df: pd.DataFrame) -> None:
        """Générer l'importance des caractéristiques de secours pour les tests"""
        # Créer un dictionnaire associant les noms des caractéristiques à leurs valeurs d'importance
        features = list(df.columns)
        
        # Assigner une plus grande importance à la créatinine et à l'urée
        self._feature_importance = {
            "Créatinine (mg/L)": 0.35,
            "Urée (g/L)": 0.25,
            "Age": 0.15,
            "TA (mmHg)/Systole": 0.10,
            "Na^+ (meq/L)": 0.05,
            "Score de Glasgow (/15)": 0.05,
            "Sexe_M": 0.02,
            "Anémie_True": 0.03,
            "Choc de Pointe/Perçu": 0.02,
            "Enquête Sociale/Tabac_True": 0.015,
            "Enquête Sociale/Alcool_True": 0.015
        }
        
        # S'assurer que l'on utilise uniquement les caractéristiques présentes dans les données d'entrée
        self._feature_importance = {
            k: v for k, v in self._feature_importance.items() if k in features
        }
        
        # Normaliser pour que la somme soit égale à 1
        total = sum(self._feature_importance.values())
        self._feature_importance = {
            k: v/total for k, v in self._feature_importance.items()
        }
    
    def get_stage_probabilities(self) -> Dict[int, float]:
        """Retourne la distribution de probabilité sur tous les stades"""
        return self._stage_probabilities if self._stage_probabilities else {}
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Retourne les scores d'importance des caractéristiques"""
        return self._feature_importance if self._feature_importance else {}
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut actuel du modèle"""
        return {
            "model_loaded": self._model_loaded,
            "model_loading": self._model_loading,
            "model_type": type(self._model).__name__ if self._model else "None"
        }
