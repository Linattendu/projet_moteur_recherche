import pandas as pd
import pickle
from datetime import datetime
import re
from src.Author import Author
from src.Frequence import Frequence 
from src.Utils import Utils
import uuid  # Pour générer des identifiants uniques


class Corpus:
    def __init__(self, nom_corpus=""):
        self.nom_corpus = nom_corpus
        self.authors = {}
        
        # dictionnaire d’indices id2doc dont les clés sont les identifiants et les valeurs
        # les objets qui représentent les documents. {"id":"doc"}
        self.id2doc = {} # 
        self.ndoc = 0
        self.naut = 0
        self.texte_concatene = None  
        
    def ajouter_document(self, doc):
        """
        Ajoute un document au corpus avec nettoyage du texte.
        """        
        
        identifiant_unique = str(uuid.uuid4())  # Génération d'un identifiant unique (UUID)
        
         # Vérification de l'unicité
        if identifiant_unique in self.id2doc:
            print(f"⚠️ Document déjà existant : {identifiant_unique}")
            return False
        
        # Ajouter le document avec l'ID généré
        self.id2doc[identifiant_unique] = doc
        self.ndoc += 1

        # Gérer l'auteur
        auteur_nom = doc.auteur
        if auteur_nom not in self.authors:
            self.authors[auteur_nom] = Author(auteur_nom)
            self.naut += 1
        
        self.authors[auteur_nom].add(identifiant_unique, doc)
        
        #print(f"✅ Document ajouté : {doc.titre} (ID: {identifiant_unique})")
        return True

    def search(self, mot_cle):
        """
        Recherche des passages contenant un mot-clé dans le texte concaténé du corpus.
        """
        # Vérification et concaténation automatique si nécessaire
        if not self.texte_concatene:
            print("🔄 Concaténation automatique du corpus...")
            self.texte_concatene = Utils.concatener_textes(self)
        
        print(f"🔍 Recherche du mot-clé : {mot_cle}\n")
        #print(f"le texte du corpus : \n {self.texte_concatene} \n" )

        # Regex : capturer 4 mots avant et après le mot-clé
        pattern = rf'(\b\w+(?:\s+\w+){{0,3}}\s+)\b{re.escape(mot_cle.lower())}\b(\s+\w+(?:\s+\w+){{0,3}})'

        
        passages = re.findall(pattern, self.texte_concatene)

        # Si aucun passage trouvé
        if not passages:
            return ["Aucun résultat trouvé."]
        
        # Reconstituer les passages capturés
        resultats = [f"{p[0]}{mot_cle}{p[1]}" for p in passages]

        # Affichage pour contrôle
        for i,passage in enumerate(resultats):
            print(f"✅ le passage {i + 1 } : {passage}\n")

        return resultats


    def concorde(self, mot_cle, taille_contexte=30):
        """
        Crée un concordancier pour un mot-clé donné à partir des textes du corpus.
        """
        # Vérification et concaténation automatique si nécessaire
        if not self.texte_concatene:
            print("🔄 Concaténation automatique du corpus...")
            self.texte_concatene = Utils.concatener_textes(self)
            
        occurences = list(re.finditer(re.escape(mot_cle), self.texte_concatene, re.IGNORECASE))

        contexte_avant = []
        mot_cle_trouve = []
        contexte_apres = []

        for occ in occurences:
            debut, fin = occ.start(), occ.end()
            mot_cle_trouve.append(self.texte_concatene[debut:fin])

            debut_contexte = max(0, debut - taille_contexte)
            contexte_avant.append(self.texte_concatene[debut_contexte:debut])

            fin_contexte = min(len(self.texte_concatene), fin + taille_contexte)
            contexte_apres.append(self.texte_concatene[fin:fin_contexte])

        df = pd.DataFrame({
            'contexte_avant': contexte_avant,
            'mot_cle_trouve': mot_cle_trouve,
            'contexte_apres': contexte_apres
        })
        return df
    
    def afficher_premiers_documents(self, n=5):
        """
        Affiche les n premiers documents du corpus.
        """
        print(f"\n📄 Affichage des {n} premiers documents du corpus :\n")
        for i, doc in enumerate(list(self.id2doc.values())[:n]):
            print(f"🔹 Document {i+1} :")
            print(f"   Titre : {doc.titre}")
            print(f"   Auteur : {doc.auteur}")
            print(f"   Date : {doc.date}")
            print(f"   URL : {doc.url}")
            print(f"   Contenu : {doc.texte}")  # Affiche seulement les 200 premiers caractères
            print("-" * 80)

    
    def stats(self, n=10):
        compteur = Frequence.compter_occurrences(self.id2doc.values())
        freq_df = pd.DataFrame(compteur.most_common(n), columns=['Mot', 'Fréquence'])
        return freq_df
    
    def trier_par_date(self, n=10):
        """
        @brief Trie les documents par date de publication.
        @param n Nombre de documents à retourner (par défaut 10).
        @return Liste des n documents les plus récents.
        """
        return sorted(self.id2doc.values(), key=lambda d: d.date, reverse=True)[:n]

    def trier_par_titre(self, n=10):
        """
        @brief Trie les documents par titre alphabétique.
        @param n Nombre de documents à retourner (par défaut 10).
        @return Liste des n premiers documents triés par titre.
        """
        return sorted(self.id2doc.values(), key=lambda d: d.titre)[:n]

    def __repr__(self):
        """
        @brief Retourne une représentation textuelle du corpus.
        @return Chaîne représentant le corpus (nom, nombre de documents et auteurs).
        """
        return f"Nom du corpus: {self.nom_corpus} - {self.ndoc} documents, {self.naut} auteurs , Texte : {self.texte_concatene}"

    def save(self, path):
        """
        @brief Retourne une représentation textuelle du corpus.
        @return Chaîne représentant le corpus (nom, nombre de documents et auteurs).
        """
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        """
        @brief Charge un corpus à partir d'un fichier pickle.
        @param path Chemin du fichier de sauvegarde.
        @return Instance de Corpus chargée.
        """
        with open(path, 'rb') as f:
            return pickle.load(f)
    

if __name__ == "__main__":
    from src.Document import Document
    
    corpus = Corpus("water")
    corpus.ajouter_document(Document("Doc1", "Auteur1", datetime.now(), "url1", 
                                     "Monitoring water quality is essential for ecosystems, ensuring the survival of aquatic life and maintaining biodiversity. By preventing pollution and detecting harmful substances early, environmental agencies can protect rivers, lakes, and oceans, preserving delicate habitats and supporting local communities that rely on these ecosystems."))
    
    corpus.ajouter_document(Document("Doc2", "Auteur2", datetime.now(), "url2", 
                                     "The preservation of water resources helps prevent droughts by enhancing groundwater recharge and promoting efficient water usage. Conservation efforts, such as reforestation and wetland restoration, play a critical role in mitigating the impacts of climate change, safeguarding future water supplies for both human populations and natural environments."))
    
    corpus.ajouter_document(Document("Doc3", "Auteur3", datetime.now(), "url3", 
                                     "Water resources are vital for agriculture, providing essential irrigation to crops and sustaining livestock. Without sufficient water, food production can significantly decline, leading to shortages and economic instability in rural communities."))

    # test de search
    reustlat_search = corpus.search("water")
    print("Résultat search : \n", reustlat_search)
    
    # Test Concorde
    resultat_concorde = corpus.concorde("resources", taille_contexte=10)
    print("Résultat concorde : \n", resultat_concorde)
    
    # Statistiques des mots
    df = corpus.stats(10)
    print("Statistiques : ", df)
    
   
