#!/usr/bin/env python3
"""
Script pour générer les rapports Evidently périodiquement.
Ce script s'exécute en boucle et génère de nouveaux rapports toutes les 5 minutes.
"""

import time
from project import create_report

def main():
    print(" Démarrage du générateur de rapports Evidently")
    print(" Les rapports seront générés toutes les 5 minutes")
    print("Les métriques seront sauvegardées dans latest_metrics.json")
    print("-" * 60)
    
    while True:
        try:
            print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} - Génération d'un nouveau rapport...")
            metrics = create_report()
            
            print(f"Rapport généré avec succès!")
            print(f" Drift global: {metrics['global_drift']}")
            print(f" Accuracy: {metrics['classification']['accuracy']:.4f}")
            print(f" F1 Score: {metrics['classification']['f1_score']:.4f}")
            
        except Exception as e:
            print(f"Erreur lors de la génération du rapport: {e}")
        
        # Attendre 5 minutes avant le prochain rapport
        print(f"\nProchain rapport dans 5 minutes...")
        time.sleep(300)  # 300 secondes = 5 minutes

if __name__ == "__main__":
    main()
