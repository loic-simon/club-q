# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division # division "réelle"
from reportlab.pdfgen.canvas import Canvas as c
from reportlab.lib.units import cm # valeur de 1 cm en points pica
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Spacer
from reportlab.platypus import Frame as F
from reportlab.platypus.flowables import Image as rlImage
from reportlab.lib.styles import getSampleStyleSheet

import csv
import glob
import pickle
from datetime import datetime,date,time

#from Tkinter import *
#import tkinter
#import tkFileDialog
#import tkMessageBox 
#import ttk
#from tkFileDialog import *
#from tkMessageBox import *
#from Tkinter import *

import random

num_voeux=1

cas_en_cours=1
nb_cas_en_cours=0

#PYTHON 3
from tkinter import * 
import tkinter.messagebox
import tkinter.filedialog
from tkinter.messagebox import *
from tkinter.filedialog import *


class eleve:
    def __init__(self, nom, prenom, promo,num,autre=0):    
        global eleveencours
        self.nom=nom
        self.prenom=prenom
        self.promo=str(int(eval(promo)))
        self.numero_tel=num
        self.listevoeux=[]
        self.indiceeleve=eleveencours       #indice de lecture de les fichiers de commandes et donc de creation des eleves. Cet indice correspond a l'ordre des fichiers de commande dans le dossier.
        eleveencours+=1   #il est incremente a chaque nouveau fichier ie nouvel eleve
        self.spectaclesattribues=[]
        self.mecontentement=0
        self.mecontentement_precedent=0
        self.mecontentement_ajoute=0
        
        if autre!=0:
            self.autre=autre
            #contient les remarques sur un élève d'ailleurs
        else:
            self.autre=0
        
    def ajoutervoeu(self,ligne):     
        "prend en argument une ligne du tableau de commandes et l'ajoute a la liste de voeux de l'eleve si le nombre de places demandees est non nul"
        k=0
        if (ligne[colnbdeplaces]!="" and etrenombre(ligne[colnbdeplaces]) and not etrenombre(ligne[colordre])):        
            print(self)
        if (ligne[colnbdeplaces]!="" and etrenombre(ligne[colnbdeplaces]) and etrenombre(ligne[colordre])):
            
            if (ligne[colnbmini]==''):      #si le nbmini est vide, on y met le nb de places demandees
                mini=eval(ligne[colnbdeplaces])
            else:
                mini=eval(ligne[colnbmini])
            v=voeux(int(eval(ligne[0])),int(eval(ligne[colnbdeplaces])),int(eval(ligne[colordre])),mini)
            if (len(self.listevoeux)==0):      #si la liste de voeux est vide, on insere le voeu
                self.listevoeux.append(v)
                
            else:                           #sinon on l'insere par ordre de priorite, la priorite 1 en premier
                k=0
                while (k<len(self.listevoeux) and self.listevoeux[k].ordre<v.ordre):
                    k+=1
                self.listevoeux.insert(k,v)
                
    
    def imprimervoeux(self): 
        "Imprime la liste de voeux de l'eleve self"
        for k in range (len(self.listevoeux)):
            print ("---------------Voeux num " + str(k+1) + "---------------------")
            print ("le titre du spectacle est " + str(self.listevoeux[k].spectacle.titre))
            print ("date: " + str(self.listevoeux[k].spectacle.date))
            print ("nb de places demandees: " + str(self.listevoeux[k].nbplaces))
    
    def __str__(self):
        "Prend un eleve en argument et renvoie la concatenation du nom et prenom au lieu de l'emplacement memoire"
        return (self.nom + " " + self.prenom)
    def __unicode__(self):                          #Ces deux autres fonctions servent a afficher listeeleves ainsi [Vidon Guillaume, Mosso Jessie]
        return (self.nom + " " + self.prenom)
    def __repr__(self):
        return (self.nom + " " + self.prenom)
    
    def update_mecontentement(self):
        self.mecontentement=self.mecontentement_precedent+self.mecontentement_ajoute    #mécontentement de la saison précédente + celui ajouté arbitrairement dans la fiche élève
                 # mécontentement lié au nombre de voeux: si l'élève a - de voeux que le nombre moyen, son mécontentement augmente, il est favorisé pour le peu de voeux qu'il a 
        self.mecontentement+=0.9**(len(self.listevoeux)-1)
        
        b=nbtotalplacesdemandees(self)
        self.mecontentement+=2/b
        if (self.promo=='135'):
            self.mecontentement=self.mecontentement+bonuspromo1A
        if (self.promo=='134'):
            self.mecontentement=self.mecontentement+bonuspromo2A
        if (self.promo=='133'):
            self.mecontentement=self.mecontentement+bonuspromo3A
        if (self.promo=='132'):
            self.mecontentement=self.mecontentement+bonuspromo4A        
        for i in range(len(self.listevoeux)):
                if (self.listevoeux[i].testattrib==1):   #cela signifie que le voeu i+1 de l'élève self lui a été attribué
                    self.mecontentement=self.mecontentement-(2*((0.5)**i))
                    
    def total_a_payer(self):
        l=liste_attributions_globale.rechercher(elv=self).liste
        s=0
        for attrib in l:
            s=s+attrib.spectacle.prix*attrib.nb_place
        return s
    
class voeux:
    def __init__(self, indexspec, nbplaces, ordre, nbplacesmin):
        self.spectacle=indiceversspect(indexspec)
        self.nbplaces=int(nbplaces)
        self.ordre=int(ordre)
        try:
            self.nbplacesmin=int(nbplacesmin)
        except:
            self.nbplacesmin=0
        self.testattrib=0
    
    def __str__(self):
        "Prend un voeu en argument et renvoie la concatenation de l'ordre de priorite, le titre, la date et le nombre de places demandees au lieu de l'emplacement memoire"
        return ("Voeu n°" + str(self.ordre) + ": " + str(self.spectacle) + " avec " + str(self.nbplaces) + " places")
    def __unicode__(self):
        return ("Voeu n°" + str(self.ordre) + ": " + str(self.spectacle) + " avec " + str(self.nbplaces) + " places")
    def __repr__(self):
        return ("Voeu n°" + str(self.ordre) + ": " + str(self.spectacle) + " avec " + str(self.nbplaces) + " places")
        
class spectacle:
    def __init__(self, indexspec, titre, lieu, date, heure, type, prix, saison, nbplaces):
        self.indexspec=indexspec
        self.titre=titre
        self.lieu=lieu
        self.date=date
        self.heure=heure
        self.type=type
        self.prix=prix
        self.saison=saison
        self.nbplaces=int(nbplaces)
        self.elevesyallant=[]
        self.nbdeplacesnonpourvues=0
        #self.nbdeplacesrestantes=self.nbplaces
    
    def nbdeplacesrestantes(self):
        s=0
        L=liste_attributions_globale.rechercher(spec=self).liste
        if len(L)>0:
            for i in L:
                s=s+i.nb_place
        return self.nbplaces-s
        
        
    def __str__(self):
        "Prend un spectacle en argument et renvoie le titre et la date au lieu de l'emplacement memoire"
        return (str(self.titre) + " le " + str(self.date) + " à " + self.heure + ", " + self.lieu)
    def __unicode__(self):
        return (str(self.titre) + " le " + str(self.date)+ " à " + self.heure + ", " + self.lieu)
    def __repr__(self):
        return (str(self.titre) + " le " + str(self.date)+ " à " + self.heure + ", " + self.lieu)
        
    def nbplacesamodifier(self):
        "Méthode d'un spectacle qui renvoie le nombre de places supplémentaires à demander ou le nombre à retirer" 
        if (nbplacesspectacle(self)>self.nbplaces):
            return ("Il faudrait demander " + str(nbplacesspectacle(self)-self.nbplaces) + " places en plus")
        else:
            return ("Il faudrait retirer " + str(self.nbplaces-nbplacesspectacle(self)) + " places")
        
class objetsasauvegarder:               #classe qui rassemble les objets a conserver: la liste d'objets eleves + la liste d'objets spectacles
    def __init__(self):
        global listeeleves
        global listespectacles
        self.eleves=listeeleves
        self.spectacles=listespectacles
        self.attribution=liste_attributions_globale
    
    def sauvegarder(self):          #sauvegarde l'objet objetsasauvegarder dans le dossier indique par lienfichiersauvegarde avec le nom indique dans lienfichiersauvegarde + date
        global lienfichiersauvegarde
        lienfichiersauvegarde = asksaveasfilename(title = "Choisir le fichier de destination de la sauvegarde :", filetypes=[("kiki", ".kiki")])
        if lienfichiersauvegarde!="":
            #date=datetime.now().isoformat().replace(":","_")
            
            if (not ".kiki" in lienfichiersauvegarde):
                lienfichiersauvegarde=lienfichiersauvegarde+".kiki"
            with open(lienfichiersauvegarde, 'wb') as fichier:
                m=pickle.Pickler(fichier)
                m.dump(self)
    
    def ouvrirsauvegarde(self,liensauvegarde):      #recupere la sauvegarde de nom "liensauvegarde" a choisir dans le dossier et modifie les variables globales listeeleves et listespectacles en fonction du contenu de la sauvegarde
        with open(liensauvegarde, 'rb') as fichier:
            m=pickle.Unpickler(fichier)
            sauvegardeimportee=m.load()
            global listeeleves
            global listespectacles
            global liste_attributions_globale
            listespectacles=sauvegardeimportee.spectacles
            listeeleves=sauvegardeimportee.eleves
            liste_attributions_globale=sauvegardeimportee.attribution
            
class attribution:
    def __init__(self, spec, elv, nb_plac,ind):
        self.spectacle=spec
        self.eleve=elv
        self.nb_place=nb_plac
        self.indice=ind
    
    def __str__(self):
        "Prend un spectacle en argument et renvoie le titre et la date au lieu de l'emplacement memoire"
        return (str(self.eleve) + " - " + str(self.nb_place) + " place(s) - " + str(self.spectacle))
    def __unicode__(self):
        return (str(self.eleve) + " - " + str(self.nb_place) + " place(s) - " + str(self.spectacle))
    def __repr__(self):
        return (str(self.eleve) + " - " + str(self.nb_place) + " place(s) - " + str(self.spectacle))
        
#On va créer une liste d'attribution globale qui permetra via des méthodes d'accéder au élèves allant à un spectacle et aux spectacles auquel assistera un élève.
class liste_attributions:
    def __init__(self):
        self.liste=[]
    
    def ajouter_n(self,spec,elv,nb_plac):
        i=len(self.liste)
        self.liste.append(attribution(spec, elv, nb_plac,i))
        #on  crée un objet attribution
        
    def ajouter_a(self,attrib):
        self.liste.append(attrib)
    
    def test(self,attrib,spec=0,elv=0,nb_pla=0):
        T=True
        if spec==0:
            if elv==0:
                if nb_pla!=0:
                    T= T and (attrib.nb_place==nb_pla)
            else:
                T=T and attrib.eleve==elv
                if nb_pla!=0:
                    T= T and (attrib.nb_place==nb_pla)
        else:
            T=T and attrib.spectacle==spec
            if elv==0:
                if nb_pla!=0:
                    T= T and (attrib.nb_place==nb_pla)
            else:
                T=T and attrib.eleve==elv
                if nb_pla!=0:
                    T= T and (attrib.nb_place==nb_pla)
                    
        return T
    
    def rechercher(self, spec=0,elv=0,nb_pla=0,indice=False):
        "renvoie la liste réduite aux champs optionnels activés"
        
        L=liste_attributions()
        
        for i in range(len(self.liste)):
            if self.test(self.liste[i],spec,elv,nb_pla):
                L.ajouter_a(self.liste[i])
        
        if indice:
            Ll=[]
            for i in L:
                Ll.append(i.indice)
            return Ll
        else:
            return L

    def supprimer(self,attrib):
        indice=attrib.indice
        k=0
        while(k<len(self.liste) and self.liste[k].indice!=indice):
            k=k+1
        
        print("Places supprimées : "+str(self.liste.pop(k)))
        
        
        
        
#--------------------------------- FONCTIONS --------------------------------------------------------

                    #----------FONCTIONS DE CONSTRUCTION----------#

def ouvrircsv(arborescence):
    import xlrd
    # ouverture du fichier Excel 
    wb = xlrd.open_workbook(arborescence)
     
    # feuilles dans le classeur
    l=wb.sheet_names()
    rep=[]
    # lecture des données dans la première feuille
    sh = wb.sheet_by_name(l[0])
    for rownum in range(sh.nrows):
        l=[]
        for i in sh.row_values(rownum):
            l.append(str(i))
        rep.append(l)
    #print(rep)
    return rep

def ouvrircsv2(arborescence):
    "Prend un fichier excel .csv et renvoie un tableau avec de type [['a','12'],['b','13']]"
    fichier=open(arborescence, "rt")
    #flux=csv.reader(fichier,delimiter=str(';'))
    tableau=[]
    print(fichier)
    for ligne in flux:
        if ligne:
            tableau.append(ligne)
    fichier.close()
    return tableau
    
def creationspect(ligne):
    "Prend une ligne avec les infos d'un spectacle et renvoie l'OBJET spectacle correspondant"
    return spectacle(eval(ligne[0]),ligne[1],ligne[2],ligne[3],ligne[4],ligne[5],float(ligne[6]),eval(ligne[7]),eval(ligne[8]))
    
def tabspectacles(lien):
    "Prend un fichier excel .csv et renvoie un tableau d'OBJETS spectacle"
    t=ouvrircsv(lien)
    
    a=[]
    for k in range(1,len(t)):           #La premiere ligne du fichier excel est reservee aux categories: titre, lieu...
        a.append(creationspect(t[k]))
    
    return a

def etrenombre(v):
    try:
        a=int(eval(v))
        return True
    except:
        return False

def lirefichecommande(arborescence):
    "Prend un fichier de commande rempli .csv et cree l'objet eleve correspondant avec son nom, prenom, promo,numero et sa liste de voeux"
    a=ouvrircsv(arborescence)                              
    b=eleve(a[lignom][colnom],a[ligprenom][colprenom],a[ligpromo][colpromo],a[ligpromo+1][colpromo])    #recupere les informations personnelles de l'eleve (nom, prenom..)
    for k in range(len(a)):
        if (a[k][0]!="" and a[k][0]!="Index" and etrenombre(a[k][0])):   #Si la premiere colonne possede un chiffre, alors il s'agit d'un spectacle et on remplit la liste de voeux
            b.ajoutervoeu(a[k])
    return b
    
def creationlisteeleves(dossiercommandes):
    t=glob.glob(dossiercommandes)           #glob.glob affiche la liste des arborescences des fichiers de commande: [/Users/jessie/...elevemachin , /Users/....elevetruc , ...]
    for k in range(len(t)):
        listeeleves.append(lirefichecommande(t[k]))   #cree les eleves+voeux correspondants aux feuilles de commande et les ajoute dans la listeeleves
    for k in listeeleves:
        k.update_mecontentement()
        
    showinfo(title="Importation terminée",message="Il y a " + str(len(listeeleves)) + " élèves.")
    
def indiceversspect(indicespectacle):
    "Prend un indice en argument et renvoie l'objet spectacle correspondant"
    for k in range (len(listespectacles)):
        if (indicespectacle==listespectacles[k].indexspec):
            return listespectacles[k]
            
def string_vers_spec(s):
    "renvoie le spectacle dont le string est la représentation supposée unique"
    k=0
    while(k<len(listespectacles) and str(listespectacles[k])!=s):
        k=k+1
    return listespectacles[k]

def affichervoeuxeleves(indice):
    "Affiche le nom, prenom, promo et voeux a partir de l'indice"
    k=0
    while (k<len(listeeleves) and indice!=listeeleves[k].indiceeleve):  #cherche l'eleve correspondant a l'indice donne en argument 
        k+=1
    o=listeeleves[k]        
    print("Nom: " + str(o.nom))
    print("Prenom: " + str(o.prenom))
    print("Promo: " + str(o.promo))
    print("Indice: " + str(indice))
    o.imprimervoeux()
    print ("ca marche :D")
    
def affichervoeuxelevesparnom(nomdefamille):
    "Affiche le nom, prenom, promo, indice et voeux a partir du nom"
    k=0
    while (k<len(listeeleves) and nomdefamille!=listeeleves[k].nom):  #cherche l'indice de l'eleve correspondant au nom donne en argument 
        k+=1
    if (k == len(listeeleves)):
        return "ce nom n'est pas dans la liste des eleves"
    else:
        h=listeeleves[k].indiceeleve
        affichervoeuxeleves(h)

def trialphabetique(liste):     
    "Trie une liste d'objets eleve par ordre alphabétique du nom"
    a=[]
    b=[]
    for j in range(len(listeeleves)):
        a.append((listeeleves[j].nom,listeeleves[j].indiceeleve))
    a=sorted(a, key=lambda eleve:eleve[0])              #liste a triée en fonction des noms de familles, mais ces noms sont attachés à un indice unique
    for i in range (len(listeeleves)):
        k=0
        while (k<len(listeeleves) and a[i][1]!=listeeleves[k].indiceeleve):  #cherche l'indice de l'eleve correspondant au nom donne en argument 
            k+=1
        b.append(listeeleves[k])
    return b

def objetavecnomprenom(nomprenom):
    "Prend en argument le string 'Mosso Jessie' et renvoie l'objet élève correspondant"
    #a=nomprenom.split()
    k=0
    while (k<len(listeeleves) and str(listeeleves[k])!=nomprenom):  #cherche l'indice de l'eleve correspondant au nom donne en argument 
        k+=1
    return listeeleves[k]
    

    

                    #----------FONCTIONS D'ANALYSE----------#    

def nbplacesspectacle(spec):
    "Prend en argument un objet spectacle et renvoie le nombre total de places demandees par les eleves pour ce spectacle"
    nb=0
    for k in range (len(listeeleves)):
        for j in range (len(listeeleves[k].listevoeux)):
            if (listeeleves[k].listevoeux[j].spectacle==spec):
                nb=nb+listeeleves[k].listevoeux[j].nbplaces
    return nb


def liste_eleve_desirant_spec(spec):
    "Prend un objet spectacle en argument et renvoie une liste de type ['Vidon Guillaume 3 places voeu1','Mosso ...']"
    i=spec.indexspec
    a=[]
    for k in range(len(listeeleves)):
        for j in range(len(listeeleves[k].listevoeux)):
            if (listeeleves[k].listevoeux[j].spectacle.indexspec==i):
                a.append(str(listeeleves[k].nom) + " " + str(listeeleves[k].prenom) + ": " + str(listeeleves[k].listevoeux[j].nbplaces) + " places - " + " Voeu n°" + str(listeeleves[k].listevoeux[j].ordre))
    return a

def nb_eleves_nayant_rien():
    nb=0
    for k in range(len(listeeleves)):
        if(len(liste_attributions_globale.rechercher(elv=listeeleves[k]).liste)==0):
            nb+=1
    return nb

def nombrevoeuxmoyen():
    cp=0    
    global listeeleves
    for k in range(len(listeeleves)):
        cp+=len(listeeleves[k].listevoeux)
    cp=cp/len(listeeleves)
    return cp                       #nb de voeux moyen

def nbtotalplacesdemandees(eleve):
    t=0
    for k in range(len(eleve.listevoeux)):
        t=t+eleve.listevoeux[k].nbplaces
    return t
    

#--------------------------------- PROGRAMME --------------------------------------------------------


                    #----------VARIABLES GLOBALES----------#
attrib_ss_conflit_done=0        

cas_en_cours=1
#lienspectacle="D:/Fichiers XS/ListeSpectaclesS1.xlsx"
#liendossiercommandeseleves="D:/Fichiers XS/Fiches/*"
lienspectacle="/Users/jessie/Documents/ESPCI/Club Q/Programme d'attribution/Version finale/ListeSpectaclesS1.xls"
liendossiercommandeseleves="/Users/jessie/Documents/ESPCI/Club Q/Programme d'attribution/Version finale/Feuilles de commandes/CSV/*"
liensauvsais=""
#Dans les fichiers de commande: (a changer si on modifie le design de la feuille de commande)
lignom=2                #repere la case ou se trouve le nom, le prenom...
colnom=2
ligprenom=3
colprenom=2
ligpromo=4
colpromo=2
colnbdeplaces=13
colordre=14
colnbmini=15

eleveencours=0

lienfichiersauvegarde="/Users/jessie/Documents/ESPCI/Club Q/Programme d'attribution/Version finale/Feuilles de commandes/Sauvegarde-"
lien_logo_q="./logo_q_couleur.jpg"

lien_logo="./espci_logo.png"

listespectacles=[]
listeeleves=[]
liste_attributions_globale=liste_attributions()
num_voeux=1

#pour le mécontentement, bonus de promo:
bonuspromo1A=1
bonuspromo2A=0.8
bonuspromo3A=0.6
bonuspromo4A=0.4

                    #-------------EXECUTION-------------#       
#listespectacles=tabspectacles(lienspectacle) #liste d'objets spectacle
#creationlisteeleves(liendossiercommandeseleves) #liste d'objets eleves

def eleves_interesses_spectacle(spec):
    "Prend un objet spectacle en argument et renvoie une liste contenant les objets eleves interesses et leurs objets voeux"
    i=spec.indexspec
    a=[]
    for k in range(len(listeeleves)):
        for j in range(len(listeeleves[k].listevoeux)):
            if (listeeleves[k].listevoeux[j].spectacle.indexspec==i):   #si le spectacle est parmis les voeux
                a.append([listeeleves[k],listeeleves[k].listevoeux])
    return a

def num_voeu_spectacle(spec,listedevoeux):
    "Prend en argument une liste de voeux et un spectacle et retourne l'objet voeu correspondant au spectacle dans la liste"
    for k in range(len(listedevoeux)):
        if (listedevoeux[k].spectacle==spec):
            return listedevoeux[k]

def tri_eleves_mecontents(listedeleves,voeu):
    "Prend en argument une liste d'élèves renvoie une liste d'objet élèves triée du plus mécontent en premier au moins mécontent en dernier, élèves dont l'ordre de voeu donné en argument n'a pas encore été pourvu"
    a=[]
    for k in range(len(listedeleves)):
        if (len(listedeleves[k].listevoeux)>=voeu and listedeleves[k].listevoeux[voeu-1].testattrib==0):
            if (len(a)==0):
                a.append(listedeleves[k])
            else: 
                i=0
                while (i<len(a) and a[i].mecontentement>listedeleves[k].mecontentement):
                    i+=1
                a.insert(i,listedeleves[k])
    return a
    
def extraction_mecontentements_egaux(voeu):
    "Prend une liste d'eleves en argument et renvoie une liste de listes d'élèves de même mécontentement [[eleve1,eleve2],[eleve...,]]"
    liste_ecart=[]
    for k in range(len(listeeleves)):       
        if k>0:
            v=abs(listeeleves[k].mecontentement-listeeleves[k-1].mecontentement)
            if v>0:
                liste_ecart.append(v)
    if len(liste_ecart)==0:
        liste_ecart=[0]
    
    listedeleve=tri_eleves_mecontents(listeeleves,voeu)
    imprim_mec(listedeleve)
    b=1
    nouvelle_plage=1
    a=[]
    
    for i in range(len(listedeleve)-1):         #on va chercher les eleves dont le mecontentement est egal pour le voeu 'voeu'
        if (listedeleve[i].mecontentement==listedeleve[i+1].mecontentement):
            if nouvelle_plage==1:
                a.append([listedeleve[i]])
                nouvelle_plage=0
            else:
                a[-1].append(listedeleve[i])
        else:
            if(i>0):
                if (listedeleve[i].mecontentement==listedeleve[i-1].mecontentement):
                    a[-1].append(listedeleve[i])
            nouvelle_plage=1
                
    if(len(listedeleve)>1):
        if(listedeleve[-2].mecontentement==listedeleve[-1].mecontentement):
            a[-1].append(listedeleve[-1])

    return a,min(liste_ecart)
                

def attribution_sans_conflit():
    "Attribue les voeux pour lesquels le nombre de places demandé est inférieur ou égal au nombre de places disponible"
    x=[]
    for k in range(len(listespectacles)):
        nbdemande=nbplacesspectacle(listespectacles[k])
        if (nbdemande<=listespectacles[k].nbplaces):  #cas ou il n'y a pas de conflit
            a=eleves_interesses_spectacle(listespectacles[k])
            for i in range (len(a)):
                eleveint=a[i][0]
                voeu=num_voeu_spectacle(listespectacles[k],a[i][1])
                # eleveint.spectaclesattribues.append("Voeu n°" + str(voeu.ordre) + " attribué: " + str(voeu.spectacle) + " avec " + str(voeu.nbplaces) + " places")
                # listespectacles[k].elevesyallant.append(eleveint)
                # listespectacles[k].nbdeplacesrestantes-=voeu.nbplaces
                eleveint.listevoeux[voeu.ordre-1].testattrib=1        #on met la variable à 1 car le voeu est attribué
                liste_attributions_globale.ajouter_n(voeu.spectacle,eleveint,voeu.nbplaces)
            #listespectacles[k].nbdeplacesnonpourvues=listespectacles[k].nbplaces-nbdemande

            
def attribution_avec_conflit(ordrevoeu):
    #il faudra faire ici une boucle pour chaque voeu --> du voeu 1 au nb max de voeux des eleves
    # for k in range(len(listeeleves)):       #On commence par updater le mécontentement de tous les élèves après l'attribution des voeux sans conflit
    #     listeeleves[k].update_mecontentement()
    l=tri_eleves_mecontents(listeeleves,ordrevoeu)
      #liste contenant les élèves triés du plus ou moins mécontent dont le voeu 1 n'a pas encore été pourvu
    #ATTENTION: IL FAUT CONSIDERER LES CAS D'EGALITE DE MECONTENTEMENT
    #En supposant qu'on ait réglé le cas d'égalité, ici on les met à la suite 
    for i in range(len(l)):
        s=l[i].listevoeux[ordrevoeu-1].spectacle
        if (l[i].listevoeux[ordrevoeu-1].nbplaces<=s.nbdeplacesrestantes()):  #on lui attribue les places s'il y en a assez
            
            # l[i].spectaclesattribues.append("Voeu n°" + str(ordrevoeu) + " attribué: " + str(s) + " avec " + str(l[i].listevoeux[ordrevoeu-1].nbplaces) + " places")
            # 
            # s.elevesyallant.append(l[i])       
            l[i].listevoeux[ordrevoeu-1].testattrib=1 
            # s.nbdeplacesrestantes=s.nbdeplacesrestantes-l[i].listevoeux[ordrevoeu-1].nbplaces
            liste_attributions_globale.ajouter_n(s,l[i],l[i].listevoeux[ordrevoeu-1].nbplaces)
        else:
            if (l[i].listevoeux[ordrevoeu-1].nbplacesmin<=s.nbdeplacesrestantes()):      
                # l[i].spectaclesattribues.append("Voeu n°" + str(ordrevoeu) + " partiellement attribué: " + str(s) + " avec " + str(s.nbdeplacesrestantes) + " places")
                # s.elevesyallant.append(l[i])       
                l[i].listevoeux[ordrevoeu-1].testattrib=1
                # s.nbdeplacesrestantes=s.nbdeplacesrestantes-l[i].listevoeux[ordrevoeu-1].nbplacesmin
                liste_attributions_globale.ajouter_n(s,l[i],s.nbdeplacesrestantes())
    for j in range(len(l)):       
        l[j].update_mecontentement()
                            



#-------------------------AFFICHAGE---------------------------
fenetre_principale = Tk()
#Creation de la fenetre

label = Label(fenetre_principale, text="Liste des spectacles") #cree une etiquette Liste des spectacles
label.pack()            #affiche l'etiquette

haut=Frame(fenetre_principale, width=500,height=500, bg='green')        #cree un premier bloc dans la fenetre principale
liste_s = Listbox(haut)                                           #cree une liste dans ce bloc

liste_s.pack(fill='x',padx=10,pady=10)                #affiche la liste et le bloc, qui se deplacent avec les 'x'
haut.pack(fill='x',padx=20,pady=20)

label = Label(fenetre_principale, text="Liste des elèves")  #cree un autre bloc contenant une liste
label.pack()

bas=Frame(fenetre_principale, width=500,height=500, bg='yellow')
recherche=Entry(bas)
recherche.pack(side='top',pady=10,padx=10,fill='x')

liste_e = Listbox(bas)
liste_e.pack(fill='x',padx=10,pady=10)
bas.pack(fill='x',padx=20,pady=20)




#-----------------FONCTIONS---------------------------------------------------------
def alert():
    filepath = askopenfilename(title="Ouvrir une image",filetypes=[('png files','.png'),('all files','.*')])
    
def eleves_sans_rien():
    fen=Tk()
    fen.title("Les élèves n'ayant aucun voeux")
    i=0
        
    for el in listeeleves:
        if len(liste_attributions_globale.rechercher(elv=el).liste)==0:
            Label(fen, text=str(el)).grid(row=i,column=0)
            i=i+1
            
def tri_voeux_(ls_lbl):
    global num_voeux
    if(num_voeux>len(listespectacles)):
        showerror(title="Plus de voeux", message="Le nombre de voeux ne peut excéder le nombre de spectacles.")
        eleves_sans_rien()
    else:
        liste_egal,ecart=extraction_mecontentements_egaux(num_voeux)
        if(len(liste_egal)>0):
            showerror(title="Encore des cas d'égalité", message="Il y a encore des cas d'égalité à traiter.")
        else:
            attribution_avec_conflit(num_voeux)
            num_voeux+=1
            liste_egal,ecart=extraction_mecontentements_egaux(num_voeux)
            global nb_cas_en_cours
            global cas_en_cours
            nb_cas_en_cours=len(liste_egal)
            if nb_cas_en_cours==0:
                cas_en_cours=0
            else:
                cas_en_cours=1
            update_tri(ls_lbl)
        

def tri_voeux_ss_conflit(ls_lbl):
    global attrib_ss_conflit_done
    attrib_ss_conflit_done=1
    attribution_sans_conflit()
    cas_en_cours=1
    for i in listeeleves:
        i.update_mecontentement()
    
    liste_egal,ecart=extraction_mecontentements_egaux(num_voeux)
    global nb_cas_en_cours
    global cas_en_cours
    nb_cas_en_cours=len(liste_egal)
    if nb_cas_en_cours==0:
        cas_en_cours=0
    else:
        cas_en_cours=1
    
    update_tri(ls_lbl)
    

def update_tri(ls_lbl):
    for i in range(len(ls_lbl)-2):
        spec=listespectacles[i]
        ls_lbl[i].configure(text=str(spec.nbdeplacesrestantes()), justify='left')
        
        rep="Attribution sans conflit non effectuée."
        if attrib_ss_conflit_done==1:
            rep="Attribution sans conflits faite."
            
        ls_lbl[-2].configure(text=rep+"\nVoeux en cours n°"+str(num_voeux)+" sur "+str(len(listespectacles))+"."+"\nNombre d'élèves sans aucune attribution : " + str(nb_eleves_nayant_rien()))
        
        # liste_egal,ecart=extraction_mecontentements_egaux(num_voeux)
        # if len(liste_egal)==0:
        #     global cas_en_cours
        #     cas_en_cours=0
        # elif cas_en_cours==0:
        #     cas_en_cours=1
        global cas_en_cours
        global nb_cas_en_cours
        if cas_en_cours>nb_cas_en_cours:
            liste_egal,ecart=extraction_mecontentements_egaux(num_voeux)
            nb_cas_en_cours=len(liste_egal)
            if nb_cas_en_cours==0:
                cas_en_cours=0
            else:
                cas_en_cours=1
        ls_lbl[-1].configure(text="Nombre de cas d'égalité : " +str(nb_cas_en_cours)+ "\nCas n°"+str(cas_en_cours)+" en cours.", justify='left')
        

def Reset(ls_lbl):
    if askokcancel(message="Le tri sera oublié ainsi que toutes les opérations manuelles effectuées. Voulez vous continuer ?"):
        global num_voeux
        num_voeux=1
        for el in listeeleves:
            for vo in el.listevoeux:
                vo.testattrib=0
                
        global liste_attributions_globale
        liste_attributions_globale=liste_attributions()
            
        global attrib_ss_conflit_done
        attrib_ss_conflit_done=0
        
        cas_en_cours=1
        update_tri(ls_lbl)
        
def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),height=200)
    
def myfunction2(event):
    canvas2.configure(scrollregion=canvas2.bbox("all"),height=300,width=300)

def aleatoire(liste):
        l=len(liste)
        ordre=list(range(1,l+1))
        deja_ordre=[]
        for i in liste:
            if i.get()!="":
                try:
                    e=int(i.get())
                except:
                    e=0
                if e in ordre:
                    ordre.remove(e)
                    deja_ordre.append(e)
        print(deja_ordre)
        for i in liste:
            try:
                e=int(i.get())
            except:
                e=0
            if not e in deja_ordre:
                if len(ordre)>0:
                    indice=random.randint(0,len(ordre)-1)
                    i.delete(0,END)
                    i.insert(0, ordre[indice])
                    ordre.remove(ordre[indice])

def non_complet(liste):
    if len(liste)>0:
        ordre=list(range(1,len(liste)+1))
        for i in liste:
            try:
                e=int(i.get())
                ordre.remove(e)
            except:
                print("exception")
                return True
        return (len(ordre)!=0)
    else:
        return True

def imprim_mec(liste):
    for i in range(len(liste)):
        print(str(liste[i]) + ", Mecontentement : "+str(liste[i].mecontentement))     

def ordonner(liste,ls_lbl,fen):
    global cas_en_cours

    if non_complet(liste):
        if askokcancel(message="Attention, la liste est non complète ou mal ordonnée. Un ajustement aléatoire sera effectué. Voulez-vous continuer ?"):
            aleatoire(liste)
        else:
            return None
            
    liste_egal,ecart=extraction_mecontentements_egaux(num_voeux)
    
    if ecart==0:
        #Tous les mécontentements sont égaux. On va les étaler en ajoutant de 1 à 0
        l=len(liste)
        for i in range(l):
            e=int(liste[i].get())
            liste_egal[0][i].mecontentement+=(1-(float(e)/l))
    else:
        ecart=float(ecart)/2
        #pour etre sur de ne géner personne
        l=len(liste)
        for i in range(l):
            e=int(liste[i].get())
            liste_egal[0][i].mecontentement+=(1-(float(e)/l))*ecart
    
    cas_en_cours+=1
    update_tri(ls_lbl)
    fen.destroy()
    cas_en_courseg(ls_lbl)
   
def cas_en_courseg(liste):
    global cas_en_cours
    
    if cas_en_cours==0:
        showinfo(message="Il n'y a plus de cas d'égalité à régler.")
    else:
        ega=Tk()
        ega.title("Gestion du cas d'égalité n°"+str(cas_en_cours))
        
        haut=Frame(ega)
        Label(haut,text="Remplissez l'ordre de priorité, 1 étant le plus prioritaire. \nLes cases vides lors de la pression du bouton Aléatoire se \nverront donner un rang aléatoire parmi ceux qu'il reste.",justify='left').pack(side='left',padx=5,pady=5)
        
        base=Frame(ega)
        
    
        
        
        #scrollbar
        global canvas2
        canvas2=Canvas(base)
        frame2=Frame(canvas2)
        myscrollbar=Scrollbar(base,orient="vertical",command=canvas2.yview)
        canvas2.configure(yscrollcommand=myscrollbar.set)
        myscrollbar.pack(side="right",fill="y")
        canvas2.pack(fill='x')
        canvas2.create_window((0,0),window=frame2,anchor='nw')
        frame2.bind("<Configure>",myfunction2)
        
        
        
        liste_egal,ecart=extraction_mecontentements_egaux(num_voeux)
        liste_entry=[]
        
        if(len(liste_egal)>0):
            for i in range(len(liste_egal[0])):
                Label(frame2,text=str(liste_egal[0][i])).grid(row=2*i,padx=10,sticky='w')
                e=Entry(frame2,width=5)
                liste_entry.append(e)
                e.grid(row=2*i,column=1,padx=10)
        
        
        f=Frame(haut)
        Button(f,text="Aléatoire",command=lambda: aleatoire(liste_entry)).pack(side='top',padx=5,pady=2)
        Button(f,text="Valider",command=lambda: ordonner(liste_entry,liste,ega)).pack(side='bottom',padx=5,pady=2)
        f.pack(side='right',padx=5,pady=5)
        
        haut.pack(side='top',padx=5,pady=5)
        
        
        base.pack(side='bottom',padx=10,pady=10,fill='x')
        update_tri(liste)
    
def tri():
    tri=Tk()
    tri.title("Gestion du tri")
    
    cas_en_cours=1
    
    gauche=Frame(tri)
    Haut= LabelFrame(gauche,text="Répartition", width=200) 
    infos=LabelFrame(gauche,text="Infos")
    caseg=LabelFrame(gauche,text="Cas d'égalité de mécontentement")
    
    
    liste_egal,ecart=extraction_mecontentements_egaux(num_voeux)
    global nb_cas_en_cours
    global cas_en_cours
    nb_cas_en_cours=len(liste_egal)
    if nb_cas_en_cours==0:
        cas_en_cours=0
    else:
        cas_en_cours=1
    # if len(liste_egal)==0:
    #     global cas_en_cours
    #     cas_en_cours=0
    # elif cas_en_cours==0:
    #     cas_en_cours=1
    nb_cas_en_coursegal=Label(caseg,text="Nombre de cas d'égalité : " +str(nb_cas_en_cours)+ "\nCas n°"+str(cas_en_cours)+" en cours.", justify='left')
    nb_cas_en_coursegal.pack(side='left',padx=5,pady=5)
    
    
    cote=LabelFrame(tri,text="Nombres de places restantes aux spectacles") 
    tri.columnconfigure(0, weight=1)
    tri.rowconfigure(0, weight=1)
    tri.columnconfigure(1, weight=2)
    tri.columnconfigure(2, weight=0)
    cote.grid(row=0,column=0, sticky="nsew");
    cote.grid_rowconfigure(0, weight=1)
    cote.grid_columnconfigure(0, weight=1)
    
    
    global canvas
    canvas=Canvas(cote)
    frame=Frame(canvas)
    
    frame.grid(row=0,column=0, sticky="nsew");
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=2)
    frame.columnconfigure(2, weight=0)
    
    myscrollbar=Scrollbar(cote,orient="vertical",command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)
    
    myscrollbar.pack(side="right",fill="y")
    canvas.pack(side="left")
    canvas.create_window((0,0),window=frame,anchor='nw')
    frame.bind("<Configure>",myfunction)

    
    rep="Attribution sans conflit non effectuée."
    if attrib_ss_conflit_done==1:
        rep="Attribution sans conflits faite."
    
    label3 = Label(infos, text=rep+"\nVoeux en cours n°"+str(num_voeux)+" sur "+str(len(listespectacles))+".\n"+"Nombre d'élèves sans aucune attribution : " + str(nb_eleves_nayant_rien()), justify='left')
    label3.pack(padx=5,pady=5,side='left')
    
    
    liste_lblframe=[]
    liste_lbl=[]
    
    for i in range(len(listespectacles)):
        spec=listespectacles[i]
        #liste_lblframe.append(Label(frame,text=spec.titre))
        Label(frame, text=spec.titre[0:min(30, len(spec.titre))]+ " :" , justify='left').grid(row=i,column=0,padx=2,sticky=W)
        liste_lbl.append(Label(frame, text=str(spec.nbdeplacesrestantes()), justify='left'))
        liste_lbl[i].grid(row=i,column=2,padx=10,sticky=W)

    

    Button(caseg, text="Traiter le cas en cours",command=lambda: cas_en_courseg(liste_lbl)).pack(padx=5,pady=5,side='right')
    Button(infos, text ='Reset',command=lambda: Reset(liste_lbl)).pack(side='right', padx=5, pady=5)
    Button(Haut, text ='Attribution des places sans conflit',command=lambda: tri_voeux_ss_conflit(liste_lbl)).pack(side=LEFT, padx=5, pady=5)
    Button(Haut, text ='Attribution du voeux en cours', command=lambda: tri_voeux_(liste_lbl)).pack(side=LEFT, padx=5, pady=5)
    
    
    
    liste_lbl.append(label3)
    liste_lbl.append(nb_cas_en_coursegal)
    
    Haut.grid(row=0,column=0,padx=20,pady=10)
    infos.grid(row=1,column=0,padx=20,pady=10)
    caseg.grid(row=2,column=0,padx=20,pady=10)
    gauche.grid(row=0,column=0,padx=20)
    cote.grid(row=0,column=1,padx=20,pady=10)
    # for i in range(len(listespectacles)):
    #     liste_lblframe[i].pack(padx=20,pady=10,side='top')
    
def trier_voeux_attribues(eleve):
    liste_a_trier=[]
    for i in eleve.spectaclesattribues:
        try:
            liste_a_trier.append([i, int(i[7:9])])
        except:
            liste_a_trier.append([i, int(i[7])])
    liste_a_trier.sort()
    
    eleve.spectaclesattribues=[]
    
    for i in range(len(liste_a_trier)):
        eleve.spectaclesattribues.append(liste_a_trier[i][0])
    

def update_listes():
    global listeeleves
    liste_s.delete(0,last='end')      #supprime ce qu'il y a dans la liste à afficher
    listeeleves=trialphabetique(listeeleves)
    for k in range(len(listespectacles)):
        liste_s.insert('end',listespectacles[k])        #remplit avec les éléments de la sauvegarde
    liste_s.pack()
    liste_e.delete(0,last='end')      
    for k in range(len(listeeleves)):
        liste_e.insert('end',listeeleves[k])
    liste_e.pack()
    
    

def charger_sauv():
    filepath = askopenfilename(title="Ouvrir une sauvegarde",filetypes=[('kiki files','.kiki'),('all files','.*')])
    if filepath!="":
        s=objetsasauvegarder()
        s.ouvrirsauvegarde(filepath)
        update_listes()
    
def creer_sauv():
    s=objetsasauvegarder()
    s.sauvegarder()
    
def recup(): #on considère que le fichier spectacle et les fiches de commandes sont toujours au même endroit 
    question=Tk()
    question.title("Récupération d'une nouvelle saison")
    
    haut=LabelFrame(question, text="Fiches élève",width=500,height=100)
    l1=Label(haut,text="Répertoire d'accès aux fiches de la nouvelle saison : \n " + liendossiercommandeseleves,justify='left')
    l1.pack(side='left',padx=5,pady=5)
    b=Button(haut, text='Modifier', command=lambda: modif_lien_fiches(l1))
    b.pack(side='right',padx=10,pady=10)
    haut.pack(padx=10,pady=10,fill='x')
    
    haut2=LabelFrame(question, text="Liste des spectacles", width=500,height=100)
    l2=Label(haut2,text="Fichier XLS des spectacles de la nouvelle saison : \n " + lienspectacle,justify='left')
    l2.pack(side='left',padx=5,pady=5)
    b=Button(haut2, text='Modifier', command= lambda: modif_lien_spectacles(l2))
    b.pack(side='right',padx=10,pady=10)
    haut2.pack(padx=10,pady=10,fill='x')
    
    haut3=LabelFrame(question, text="Saison précédente", width=500,height=100)
    l3=Label(haut3,text="Lien vers la sauvegarde de la saison précédente si elle existe : \n " + liensauvsais,justify='left')
    l3.pack(side='left',padx=5,pady=5)
    b=Button(haut3, text='Modifier', command= lambda: modif_lien_sauv(l3))
    b.pack(side='right',padx=10,pady=10)
    haut3.pack(padx=10,pady=10,fill='x')
    
    haut4=Frame(question, width=500,height=100)
    Button(haut4, text="Quitter", command=question.destroy).pack(side='left',padx=10)
    Button(haut4, text="Valider", command=lambda: valider(question)).pack(side='right',padx=10)
    haut4.pack(padx=10,pady=10,fill='x')
    

def valider(fen):
    fen.destroy()
    global listespectacles
    global listeeleves
    global liensauvsais
    listespectacles=[]
    listeeleves=[]
    if pre_analyse_elv(liendossiercommandeseleves):
        listespectacles=tabspectacles(lienspectacle)        #liste d'objets spectacle
        creationlisteeleves(liendossiercommandeseleves)     #liste d'objets eleves
        
        #Récupération de l'ancien mécontentement
        if (liensauvsais!=""):
            with open(liensauvsais, 'rb') as fichier:
                m=pickle.Unpickler(fichier)
                sauvegardeimportee=m.load()
                
                anciens_eleves=sauvegardeimportee.eleves
                
                for eleve in listeeleves:
                    
                    i=-1
                    trouve_ancien=False
                    while((not trouve_ancien) and (i<len(anciens_eleves))):
                        i=i+1
                        if(anciens_eleves[i].prenom.lower()==eleve.prenom.lower() and anciens_eleves[i].nom.lower()==eleve.nom.lower()):
                            trouve_ancien=True
                        
                    if trouve_ancien:
                        eleve.mecontentement_precedent=anciens_eleves[i].mecontentement
    
        update_listes()

def remplirlistbox(listebox,items):
    "items est une liste à remplir dans listebox"
    vider(listebox)
    for i in range(len(items)):
        listebox.insert(i, items[i])

def pdf_spectacles():
    #Attention ! renomer les importations de Frame en F et Canvas en  c

    lien_pdf=askdirectory(title='Selectionnez un dossier où les fiches spectacles seront exportées :')
    if lien_pdf!="":
        
        
        for spec in listespectacles:
            
            can = c("{0}".format(lien_pdf+"/"+spec.titre+".pdf"), pagesize=A4)
            styles = getSampleStyleSheet() 
            styleN =styles["Normal"]
            can.setFont("Times-Bold", 18)
            
            description=[]
            liste_eleves=[]
            texte=["Titre : ","Lieu : ", "Heure : ", "Date : ","Nombre de places disponibles : "]
            texte[0]=texte[0]+"<b>"+spec.titre+"</b>"
            texte[1]=texte[1]+"<b>"+spec.lieu+"</b>"
            texte[2]=texte[2]+"<b>"+spec.heure+"</b>"
            texte[3]=texte[3]+"<b>"+spec.date+"</b>"
            texte[4]=texte[4]+"<b>"+str(spec.nbplaces)+"</b>"
            
            eleves=[]
            L=liste_attributions_globale.rechercher(spec=spec).liste
            for el in L:
                ele=el.eleve
                if ele.autre==0:
                    eleves.append(str(ele)+", "+ele.promo+", "+ele.numero_tel+" - "+str(el.nb_place)+" place(s)")
                else:
                    eleves.append(str(ele)+", "+ele.autre+", "+ele.numero_tel+" - "+str(el.nb_place)+" place(s)")
            
            for txt in texte:
                description.append(Paragraph(txt, styleN))
                description.append(Spacer(1, .2*cm)) 
                
            for txt in eleves:
                liste_eleves.append(Paragraph(txt, styleN))
                liste_eleves.append(Spacer(1, .2*cm)) 
            
            cH =F(1*cm, 23.5*cm, 19*cm, 3.5*cm, showBoundary =1)
            cH.addFromList(description, can)
            
            hauteur=21.5
            ordonnee=22.5-hauteur
            cb =F(1*cm, ordonnee*cm, 19*cm, hauteur*cm, showBoundary =1)
            cb.addFromList(liste_eleves, can)
            
            global lien_logo
            global lien_logo_q
            #dX, dY =can.drawImage(lien_logo, 15*cm, 27.8*cm,width=(4.9)*cm, height=1*cm, mask="auto")
            dX, dY =can.drawImage(lien_logo_q, 15*cm, 24.5*cm,width=(4)*cm, height=4*cm, mask="auto")
            
            can.setFont("Times-Bold", 18)
            can.drawString(1*cm, 28*cm, "Compte-rendu : " + spec.titre)
            can.showPage()
            
            
            
            description=[]
            liste_eleves=[]
            texte=["Titre : ","Lieu : ", "Heure : ", "Date : ","Nombre de places disponibles : "]
            texte[0]=texte[0]+"<b>"+spec.titre+"</b>"
            texte[1]=texte[1]+"<b>"+spec.lieu+"</b>"
            texte[2]=texte[2]+"<b>"+spec.heure+"</b>"
            texte[3]=texte[3]+"<b>"+spec.date+"</b>"
            texte[4]=texte[4]+"<b>"+str(spec.nbplaces)+"</b>"
            
            
            Liste_voeux=[]
            Liste_eleves=[]
            for i in range(len(listeeleves)):
                for j in listeeleves[i].listevoeux:
                    if j.spectacle==spec:
                        if j.testattrib==0:
                            Liste_voeux.append(j)
                            Liste_eleves.append(listeeleves[i])
                            
                            
            
            
            if( len(Liste_eleves)>0 and len(Liste_voeux)>0):
                l_affich=["Liste d'attente."]
                liste_triee=[[Liste_eleves[0]],[Liste_voeux[0]]]
            
                
                for i in range(1,len(Liste_eleves)):
                    k=0
                    while (k<i) and (liste_triee[0][k].mecontentement>Liste_eleves[i].mecontentement):
                        k=k+1
                        #print(k)
                    liste_triee[0].insert(k,Liste_eleves[i])
                    liste_triee[1].insert(k,Liste_voeux[i])
                
                
                for i in range(len(Liste_voeux)):
                    l_affich.append("M:"+str(round(liste_triee[0][i].mecontentement,2))+" - "+str(liste_triee[0][i])+" - "+ str(liste_triee[1][i].nbplaces)+" place(s) "+"("+str(liste_triee[1][i].nbplacesmin)+" min)"+"- Voeu n°"+str(liste_triee[1][i].ordre))
            else:
                l_affich=["Pas de liste d'attente."]
            
            eleves=l_affich
            
            
            for txt in texte:
                description.append(Paragraph(txt, styleN))
                description.append(Spacer(1, .2*cm)) 
                
            for txt in eleves:
                liste_eleves.append(Paragraph(txt, styleN))
                liste_eleves.append(Spacer(1, .2*cm)) 
            
            cH =F(1*cm, 23.5*cm, 19*cm, 3.5*cm, showBoundary =1)
            cH.addFromList(description, can)
            
            hauteur=21.5
            ordonnee=22.5-hauteur
            cb =F(1*cm, ordonnee*cm, 19*cm, hauteur*cm, showBoundary =1)
            cb.addFromList(liste_eleves, can)
            
            global lien_logo
            global lien_logo_q
            #dX, dY =can.drawImage(lien_logo, 15*cm, 27.8*cm,width=(4.9)*cm, height=1*cm, mask="auto")
            #dX, dY =can.drawImage(lien_logo_q, 15*cm, 24.5*cm,width=(4)*cm, height=4*cm, mask="auto")
            
            can.setFont("Times-Bold", 18)
            can.drawString(1*cm, 28*cm, "Compte-rendu : " + spec.titre+" - Liste d'attente")
            can.showPage()
             
            can.save()
        
def pdf_eleve(eleve, lien_dossier):
    #Attention ! renomer les importations de Frame en F et Canvas en  c
    if lien_dossier!="":
        trier_voeux_attribues(eleve)
        
        can = c("{0}".format(lien_dossier+"/"+eleve.nom+"_"+eleve.prenom+".pdf"), pagesize=A4)
        styles = getSampleStyleSheet() 
        styleN =styles["Normal"]
        can.setFont("Times-Bold", 18)
        
       
        description=[]
        liste_spec=[]
        texte=["Nom : ", "Prénom : ", "Promo : ","Numéro de téléphone : "]
        texte[0]=texte[0]+"<b>"+eleve.nom+"</b>"
        texte[1]=texte[1]+"<b>"+eleve.prenom+"</b>"
        if eleve.autre==0:
            texte[2]=texte[2]+"<b>"+eleve.promo+"</b>"
        else:
            texte[2]=texte[2]+"<b>"+eleve.autre+"</b>"
        texte[3]=texte[3]+"<b>"+eleve.numero_tel+"</b>"
        
        spec=[]
        L=liste_attributions_globale.rechercher(elv=eleve).liste
        for el in L:
            spec.append(str(el.spectacle)+" - "+str(el.nb_place)+" place(s) - "+str(el.spectacle.prix)+"€")
        spec.append("-"*158)
        spec.append("Total à payer : "+str(eleve.total_a_payer())+"€.")
        
        for txt in texte:
            description.append(Paragraph(txt, styleN))
            description.append(Spacer(1, .2*cm)) 
            
        for txt in spec:
            liste_spec.append(Paragraph(txt, styleN))
            liste_spec.append(Spacer(1, .2*cm)) 
        
        cH =F(1*cm, 23.5*cm, 19*cm, 3*cm, showBoundary =1)
        cH.addFromList(description, can)
        
        #hauteur=len(spec)*0.75
        hauteur=22
        ordonnee=23-hauteur
        cb =F(1*cm, ordonnee*cm, 19*cm, hauteur*cm, showBoundary =1)
        cb.addFromList(liste_spec, can)
        
        global lien_logo
        global lien_logo_q
        #dX, dY =can.drawImage(lien_logo, 15*cm, 27.8*cm,width=(4.9)*cm, height=1*cm, mask="auto")
        dX, dY =can.drawImage(lien_logo_q, 15*cm, 24.5*cm,width=(4)*cm, height=4*cm, mask="auto")
        
        can.setFont("Times-Bold", 18)
        can.drawString(1*cm, 28*cm, "Compte-rendu : " + eleve.prenom + " "+ eleve.nom)
        can.showPage() 
        can.save()
   
def exporter_fiches_eleves():
    lien_pdf=askdirectory(title='Selectionnez un dossier pour exporter les fiches pdf individuelles :')
    if lien_pdf!="":
        for eleves in listeeleves:
            pdf_eleve(eleves, lien_pdf)
    
def modif_lien_fiches(label):
    global liendossiercommandeseleves
    filepath=askdirectory(title="Répertoire d'accès aux fiches élèves XLSX. Ce repertoire doit contenir UNIQUEMENT les fiches des élèves.")
    if filepath!="":
        liendossiercommandeseleves = filepath+"/*"
        update_edit(label,1)

def modif_lien_spectacles(label):
    global lienspectacle
    filepath=askopenfilename(title="Fichier XLSX des spectacles.")
    if filepath!="":
        lienspectacle = filepath
        update_edit(label,2)
  
def modif_lien_sauv(label):
    global liensauvsais
    filepath=askopenfilename(title="Fichier .kiki de la sauvegarde de la saison précédente.")
    if filepath!="":
        liensauvsais = filepath
        update_edit(label,3)  
    
def update_edit(label,type):
    if type==1:
        label.configure(text="Répertoire d'accès aux fiches reçues : \n " + liendossiercommandeseleves,justify='left')
    elif type==2:
        label.configure(text="Fichier XLSX des spectacles : \n " + lienspectacle,justify='left')
    elif type==3:
        label.configure(text="Lien vers la sauvegarde de la saison précédente si elle existe : \n " + liensauvsais)
        
def edit_var_glob():
    fene=Tk()
    
    haut=Frame(fene, width=500,height=100)
    l1=Label(haut,text="Répertoire d'accès aux fiches reçues : \n " + liendossiercommandeseleves,justify='left')
    l1.pack(side='left',padx=5,pady=5)
    b=Button(haut, text='Modifier', command=lambda: modif_lien_fiches(l1))
    b.pack(side='right',padx=10,pady=10)
    haut.pack(padx=10,pady=10)
    
    haut2=Frame(fene, width=500,height=100)
    l2=Label(haut2,text="Fichier XLS des spectacles : \n " + lienspectacle,justify='left')
    l2.pack(side='left',padx=5,pady=5)
    b=Button(haut2, text='Modifier', command= lambda: modif_lien_spectacles(l2))
    b.pack(side='right',padx=10,pady=10)
    haut2.pack(padx=10,pady=10)
    
def fiche_eleve(event):
    eleve=objetavecnomprenom(liste_e.get(liste_e.curselection()))
    #eleve=listeeleves[liste_e.curselection()[0]]
    fen_ele=Tk()
    fen_ele.title("Fiche élève : " + eleve.prenom + " " + eleve.nom)
    
    haut=Frame(fen_ele)
    infos=LabelFrame(haut,text="Infos")
    
    gauche=Frame(infos)
    l1=Label(gauche,text="Nom : "+eleve.nom,justify='left')
    l1.pack()
    
    l2=Label(gauche,text="Prénom : "+eleve.prenom)
    l2.pack()
    
    if eleve.autre==0:
        l3=Label(gauche,text="Promo : "+eleve.promo)
        l3.pack()
    else:
        l3=Label(gauche,text="Remarques : "+eleve.autre)
        l3.pack()
    gauche.pack(side='left',pady=5,padx=10)
    
    Button(infos,text="Imprimer fiche",command=lambda: pdf_eleve(eleve,askdirectory(title='Selectionnez un dossier pour exporter la fiche pdf de ' + eleve.prenom+" :"))).pack(side='right',padx=10)
    
    infos.pack(padx=10,pady=10,side='top',fill='x')
    
   
    mec=LabelFrame(haut,text="Mécontentement")    
    l31=Label(mec,text="Ancien Mécontentement : "+str(eleve.mecontentement_precedent),justify='left')
    l31.pack(side='top')
    
    l32=Label(mec,text="Mécontentement ajouté enregistré : "+ str(eleve.mecontentement_ajoute))
    l32.pack(side='left',padx=5)
    
    value2 = StringVar() 

    entree = Entry(mec, textvariable=value2, width=5)
    entree.bind("<Return>",lambda event: update_mec_aj(event,eleve,entree,l32))
    entree.pack(side='right',padx=3,pady=3)
    
    mec.pack(padx=10,pady=10,side='bottom',fill='x')
    
    haut.pack(padx=10,side='top')
    
    bas=Frame(fen_ele)
    l4=Label(bas,text="Liste de voeux : ")
    l4.pack()
    
    
    liste_voeux=Listbox(bas,height=6)
    remplirlistbox(liste_voeux, eleve.listevoeux)
    liste_voeux.pack(fill='x',padx=10,pady=10)

    l5=Label(bas,text="Liste de places attribuées : ")
    l5.pack()
    
    liste_attrib=Listbox(bas,height=6)
    #remplirlistbox(liste_attrib, eleve.spectaclesattribues)
    remplirlistbox(liste_attrib, liste_attributions_globale.rechercher(elv=eleve).liste)
    liste_attrib.pack(fill='x',padx=10,pady=10)
    liste_attrib.bind("<Double-Button-1>",lambda event: modifplace(liste_attrib,"eleve",eleve=eleve))
    
    bas.pack(padx=10,side='bottom',fill='x')
    
    
    bas2=Frame(fen_ele)
    Button(bas2, text="Accorder un voeu",command=lambda: accorder_voeu(liste_attrib,eleve)).grid(row=0,column=0,padx=5)
    Button(bas2, text="Modifier\Supprimer une place",command=lambda: modifplace(liste_attrib,"eleve",eleve=eleve)).grid(row=0,column=1,padx=5)
    
    bas2.pack(pady=5,padx=5)


def update_mec_aj(event,el,entr,lbl):
    if entr.get()!="":
        el.mecontentement_ajoute=float(entr.get())
    else:
        el.mecontentement_ajoute=0
    el.update_mecontentement()
    lbl.configure(text="Mécontentement ajouté enregistré : "+ str(el.mecontentement_ajoute))

def fiche_spec(event):
    spec=string_vers_spec(liste_s.get(liste_s.curselection()))
    
    fen_ele=Tk()
    fen_ele.title("Fiche spectacle : "+ spec.titre)
    
    haut=LabelFrame(fen_ele,text="Infos")
    haut.pack(pady=5,padx=5)
    l1=Label(haut,text="Titre : "+spec.titre)
    l1.grid(row=0,column=0,padx=5,pady=2)
    
    l12=Label(haut,text="Lieu : "+spec.lieu)
    l12.grid(row=1,column=0,padx=5,pady=2)
    
    l2=Label(haut,text="Date : "+spec.date)
    l2.grid(row=2,column=0,padx=5,pady=2)
    
    l3=Label(haut,text="Heure : "+spec.heure)
    l3.grid(row=3,column=0,padx=5,pady=2)
    
    l31=Label(haut,text="Nombre de places à distribuer : "+str(spec.nbplaces))
    l31.grid(row=0,column=1,padx=5,pady=2)
    
    l311=Label(haut,text="Nombre total de places demandées : "+str(nbplacesspectacle(spec)))
    l311.grid(row=1,column=1,padx=5,pady=2)
    
    l312=Label(haut,text="Nombre total de places restantes : "+str(spec.nbdeplacesrestantes()))
    l312.grid(row=2,column=1,padx=5,pady=2)
    
    l32=Label(haut,text="Type : "+spec.type)
    l32.grid(row=3,column=1,padx=5,pady=2)
    
    l33=Label(haut,text="Prix : "+str(spec.prix)+" €")
    l33.grid(row=4,column=1,padx=5,pady=2)
    
    l34=Label(haut,text="Saison : "+str(spec.saison))
    l34.grid(row=4,column=0,padx=5,pady=2)
    
    mil=Frame(fen_ele)
    Button(mil,text="Ajouter l'élève sélectionné", command=lambda:ajouter_el_sel(spec, liste_voeux,liste_attrib,l312)).grid(row=0,column=0,padx=5,pady=2)
    Button(mil,text="Modifier\Supprimer une place", command=lambda:modifplace(liste_attrib,"spec",spec=spec,l=l312)).grid(row=0,column=1,padx=5,pady=2)
    Button(mil,text="Déçus",command=lambda:decu(spec)).grid(row=0,column=2,padx=5,pady=2)
    mil.pack()
    l4=Label(fen_ele,text="Liste des élèves désirant des places : ")
    l4.pack()
    
    liste_voeux=Listbox(fen_ele,height=7)
    laf=liste_eleve_desirant_spec(spec)
    remplirlistbox(liste_voeux,laf)
    liste_voeux.pack(fill='x',padx=10,pady=10)
    
    l5=Label(fen_ele,text="Liste des élèves sélectionnés : ")
    l5.pack()
    
    liste_attrib=Listbox(fen_ele,height=7)
    remplirlistbox(liste_attrib,liste_attributions_globale.rechercher(spec=spec).liste)
    liste_attrib.pack(fill='x',padx=10,pady=10)
    liste_attrib.bind("<Double-Button-1>",lambda event: modifplace(liste_attrib,"spec",spec=spec,l=l312))

    
def cherche(liste,element):
    "renvoie la liste qui contient tous les éléments suceptible de contenir elemnt"
    l=[]
    for i in range(len(liste)):
        if element.lower() in liste[i].lower():
            l.append(liste[i])
    return l

def vider(listbox):
    listbox.delete(0,last='end') 
    
def frecherche(event):
    elmt=recherche.get()
    if elmt!="":
        vider(liste_e)
        remplirlistbox(liste_e,listeeleves)
        liste=liste_e.get(0,END)
        vider(liste_e)
        remplirlistbox(liste_e,cherche(liste,elmt))
    else:
        vider(liste_e)
        remplirlistbox(liste_e,listeeleves)
        
def test_fiche(lien):
    "teste si la fiche eleve donnée par le lien est conforme au programme"
    print('hello')

def ajouter_el_sel(spec, listebox,liste_actualiser,l):
    elev=listebox.curselection()
    if(elev==()):
        showerror(title="Erreur", message="Vous n'avez pas sélectionné d'élève.")
    else:
        
        indice_el=int(elev[0])
        indice_spec=spec.indexspec
        n=0
        k=0
        ele_en_cours=0
        voeux=0
        
        while( k < len(listeeleves) and n<=indice_el):
            for j in range(len(listeeleves[k].listevoeux)):
                if (listeeleves[k].listevoeux[j].spectacle.indexspec==indice_spec):
                    ele_en_cours=listeeleves[k]
                    voeux=listeeleves[k].listevoeux[j]
                    n=n+1
            k=k+1
        
        #ele en cours contient l'élève qui a été sélectionné. Reste à lui ajouter le spectacle avec le bon nombre de place
        
        if(len(liste_attributions_globale.rechercher(spec=spec,elv=ele_en_cours).liste)>0):
            if askyesno(title="Erreur", message="L'élève selectionné a déjà obtenu des places pour ce spectacle. Voulez-vous modifier son attribution ?"):
                L=liste_attributions_globale.rechercher(spec=spec).liste
                m=0
                for i in range(len(L)):
                    if L[i].eleve==ele_en_cours:
                        m=i
                liste_actualiser.focus()
                liste_actualiser.selection_set(m)
                modifplace(liste_actualiser,"spec",spec=spec,l=l)
        else:
        
            confirm=Tk()
            confirm.title("Confirmation d'ajout")
            gauche=Frame(confirm)
            gauche.pack(side='left',padx=5,pady=5)
            Label(gauche, text="Vous allez ajouter l'élève : "+ str(ele_en_cours),justify='left').grid(row=0,column=0,padx=5)
            Label(gauche, text="Au spectacle : "+ spec.titre,justify='left').grid(row=1,column=0)
            Label(gauche, text="Son voeux est d'avoir "+ str(voeux.nbplaces)+" place(s) et au minimum "+str(voeux.nbplacesmin)+" places.",padx=5,justify='left').grid(row=2,column=0)
            
            accord=Frame(gauche)
            accord.grid(row=3,column=0)
            Label(accord, text="Vous lui en accordez : ",justify='left').grid(row=0,column=0,padx=5)
            e=Entry(accord)
            e.grid(row=0,column=1,padx=5)
            e.bind("<Return>",lambda event:ajouter_el_sel_valider(ele_en_cours,spec,e,confirm,voeux,liste_actualiser,l))
            
            droite=Frame(confirm)
            droite.pack(side='right',padx=5,pady=5)
            Button(droite, text="Annuler",command=confirm.destroy).grid(row=0,column=0,padx=5,pady=5)
            Button(droite, text="Valider",command=lambda:ajouter_el_sel_valider(ele_en_cours,spec,e,confirm,voeux,liste_actualiser,l)).grid(row=1,column=0,padx=5,pady=5)
            

def ajouter_el_sel_valider(ele_en_cours,spec,e,fen,voeu,liste_act,l):
    try:
        nb=int(e.get())
        fen.destroy()
        liste_attributions_globale.ajouter_n(spec,ele_en_cours,nb)
        voeu.testattrib=1
        ele_en_cours.update_mecontentement()
        #actualistation de l'affichage
        remplirlistbox(liste_act,liste_attributions_globale.rechercher(spec=spec).liste)
        l.configure(text="Nombre total de places restantes : "+str(spec.nbdeplacesrestantes()))
    except:
        showerror(title="Erreur", message="Ce n'est pas un nombre de places valide !")
    
def accorder_voeu(liste_attrib,eleve):
    fen_v=Tk()
    fen_v.title("Accorder un voeu")

    Label(fen_v,text="Choissisez le spectacle à accorder :").pack(padx=5,pady=2)
    
    OPTIONS=listespectacles.copy()
    spec_def = StringVar(fen_v)
    spec_def.set(OPTIONS[0])
    w = OptionMenu(fen_v, spec_def,*OPTIONS)
    w.pack(padx=5,pady=2)
    
    Label(fen_v,text="Choissisez le nombre de places à accorder :").pack(padx=5,pady=2)
    e=Entry(fen_v)
    e.pack(padx=5,pady=2)
    e.bind("<Return>",lambda event:a_voeu_valider(fen_v,eleve,spec_def,e,liste_attrib))
    
    basv=Frame(fen_v)
    Button(basv,text="Annuler",command=fen_v.destroy).grid(row=0,column=0,padx=3)
    Button(basv,text="Valider",command=lambda:a_voeu_valider(fen_v,eleve,spec_def,e,liste_attrib)).grid(row=0,column=1,padx=3)
    basv.pack(pady=2)
    
def a_voeu_valider(fene,eleve,spec,nb_place,listebox):
    spec=string_vers_spec(spec.get())
    try:
        nb=int(nb_place.get())
        liste_attributions_globale.ajouter_n(spec,eleve,nb)
        remplirlistbox(listebox, liste_attributions_globale.rechercher(elv=eleve).liste)
        fene.destroy()
        
        t=0
        indice=0
        for i in range(len(eleve.listevoeux)):
            if (eleve.listevoeux[i].spectacle==spec):
                t=1
                indice=i
        if t==1:
            eleve.listevoeux[indice].testattrib=1
            eleve.update_mecontentement()
    except:
        showerror(title="Erreur",message="Ce n'est pas un nombre de places valide dalida!")
    
def modifplace(listebox,typee,eleve=0,spec=0,l=0):
    attrib=listebox.curselection()
    
    if attrib==():
        showerror(title="Erreur",message="Vous n'avez pas sélectionné de place à modifier !")
    else:
        attrib=attrib[0]
        if(eleve==0):
            attrib=liste_attributions_globale.rechercher(spec=spec).liste[attrib]
        else:
            attrib=liste_attributions_globale.rechercher(elv=eleve).liste[attrib]
        
        modif=Tk()
        modif.title("Modification de l'attribution")
        
        Label(modif,text=str(attrib)).pack(padx=5,pady=5)
        mil=Frame(modif)
        mil.pack(padx=5,pady=5)
        Label(mil,text="Nouveau nombre de place :").grid(row=0,column=0,padx=2)
        e=Entry(mil,width=10)
        e.grid(row=0,column=1,padx=2)
        e.bind("<Return>",lambda event:valider_nb_place(attrib,modif,listebox,typee,e,lab=l))
        
        bas=Frame(modif)
        bas.pack(padx=2,pady=5)
        Button(bas,text="Annuler",command=modif.destroy).grid(row=0,column=0,padx=2)
        Button(bas,text="Valider le nombre de places",command=lambda: valider_nb_place(attrib,modif,listebox,typee,e,lab=l)).grid(row=0,column=1,padx=2)
        Button(bas,text="Supprimer",command=lambda: supprimer(attrib,modif,listebox,typee,lab=l)).grid(row=0,column=2,padx=2)

def valider_nb_place(attrib,fenetre,listebox,type,e,lab=0):
    try:
        nb=int(e.get())
        attrib.nb_place=nb
        fenetre.destroy()
        if type=="eleve":
            remplirlistbox(listebox,liste_attributions_globale.rechercher(elv=attrib.eleve).liste)
        else:
            remplirlistbox(listebox,liste_attributions_globale.rechercher(spec=attrib.spectacle).liste)
            lab.configure(text="Nombre total de places restantes : "+str(attrib.spectacle.nbdeplacesrestantes()))
    except:
        showerror(title="Erreur",message="Vous n'avez pas entré un nombre valide de places !")
    
def supprimer(attrib,fenetre,listebox,typee,lab=0):
    liste_attributions_globale.supprimer(attrib)
    fenetre.destroy()
    if typee=="eleve":
        remplirlistbox(listebox,liste_attributions_globale.rechercher(elv=attrib.eleve).liste)
    else:
        remplirlistbox(listebox,liste_attributions_globale.rechercher(spec=attrib.spectacle).liste)
    
    
    t,ind=0,0
    for i in range(len(attrib.eleve.listevoeux)):
        if attrib.eleve.listevoeux[i].spectacle==attrib.spectacle:
            t=1
            ind=i
    if t==1:
        attrib.eleve.listevoeux[ind].testattrib=0
        
    if lab!=0:
        lab.configure(text="Nombre total de places restantes : "+str(attrib.spectacle.nbdeplacesrestantes()))
        
    attrib.eleve.update_mecontentement()
    

def decu(spect):
    decu=Tk()
    decu.title("Déçus de "+spect.titre)
    
    Label(decu,text="Les élèves suivants n'ont pas reçu satisfaction pour ce spectacle :").pack(padx=5,pady=5)
    el_decus=Listbox(decu)
    
    Liste_voeux=[]
    Liste_eleves=[]
    for i in range(len(listeeleves)):
        for j in listeeleves[i].listevoeux:
            if j.spectacle==spect:
                if j.testattrib==0:
                    Liste_voeux.append(j)
                    Liste_eleves.append(listeeleves[i])
    
    liste_triee=[[Liste_eleves[0]],[Liste_voeux[0]]]

    
    for i in range(1,len(Liste_eleves)):
        k=0
        while (k<i) and (liste_triee[0][k].mecontentement>Liste_eleves[i].mecontentement):
            k=k+1
            print(k)
        liste_triee[0].insert(k,Liste_eleves[i])
        liste_triee[1].insert(k,Liste_voeux[i])
    
    l_affich=[]
    for i in range(len(Liste_voeux)):
        l_affich.append("M:"+str(liste_triee[0][i].mecontentement)+" - "+str(liste_triee[0][i])+" - "+ str(liste_triee[1][i].nbplaces)+" place(s) "+"("+str(liste_triee[1][i].nbplacesmin)+" min)"+"- Voeu n°"+str(liste_triee[1][i].ordre))
    
    remplirlistbox(el_decus,l_affich)
    el_decus.pack(padx=10,pady=5,fill='x')
    
    
def pre_analyse_elv(dossiercommandes):
    test=[]
    pb=[]
    t=glob.glob(dossiercommandes)           #glob.glob affiche la liste des arborescences des fichiers de commande: [/Users/jessie/...elevemachin , /Users/....elevetruc , ...]
    for k in range(len(t)):
        try:
              #cree les eleves+voeux correspondants aux feuilles de commande et les ajoute dans la listeeleves
            a=ouvrircsv(t[k])                              
            b=eleve(a[lignom][colnom],a[ligprenom][colprenom],a[ligpromo][colpromo],a[ligpromo+1][colpromo])    #recupere les informations personnelles de l'eleve (nom, prenom..)
            
            ordre_prio=[]
            
            for j in range(len(a)):
                if (a[j][0]!="" and a[j][0]!="Index" and etrenombre(a[j][0])):   #Si la premiere colonne possede un chiffre, alors il s'agit d'un spectacle et on remplit la liste de voeux
                    ligne=a[j]
                    if ligne[colnbdeplaces]!="" and ((not etrenombre(ligne[colnbdeplaces])) or (not etrenombre(ligne[colordre]))):
                        pb.append(t[k].split("/")[-1]+" - Ligne " + str(1+j))
                    elif ligne[colnbdeplaces]!="":
                        
                        ordre_prio.append(int(eval(ligne[colordre])))
            

            for ordre in range(1,len(ordre_prio)+1):
                try:
                    ordre_prio.remove(ordre)
                except:
                    pb.append(t[k].split("/")[-1]+" - Problème d'ordre des voeux")
                    
            test.append("ok") 
        except:
            pb.append(t[k].split("/")[-1] + " - Problème dans les données de l'élève")
    # rap=Tk()
    # rap.title("Rapport de pré-analyse des fichiers élèves")
    
    texte="La pré-analyse des fichiers élèves est terminée."
    
    if(len(pb)>0):
        texte=texte+" \rIl y a eu un problème avec les fichiers suivants : "
        for i in pb:
            texte=texte+" \r"+ i
        return showerror(title="Erreur détectée", message=texte)!='ok'
    else:
        texte=texte+ " \rIl n'y a eu aucun problème. "+str(len(test))+" élèves ont été ajoutés."
        return showinfo(title="Pas d'erreurs détectées",message=texte)=='ok'
        
def nouvel_eleve():
    nv=Tk()
    nv.title("Ajouter un élève")
    
    Label(nv,text="Nom : ").grid(row=0,column=0,padx=2,pady=2)
    Label(nv,text="Prénom : ").grid(row=1,column=0,padx=2,pady=2)
    Label(nv,text="Numéro de téléphone : ").grid(row=2,column=0,padx=2,pady=2)
    Label(nv,text="Remarques : ").grid(row=3,column=0,padx=2,pady=2)
    
    n=Entry(nv)
    n.grid(row=0,column=1,padx=2,pady=2)
    p=Entry(nv)
    p.grid(row=1,column=1,padx=2,pady=2)
    num=Entry(nv)
    num.grid(row=2,column=1,padx=2,pady=2)
    rem=Entry(nv)
    rem.grid(row=3,column=1,padx=2,pady=2)
    
    Button(nv, text="Annuler", command=nv.destroy).grid(row=4,column=0,padx=2,pady=2)
    Button(nv, text="Valider", command=lambda: nouvel_eleve_valider(n.get(),p.get(),num.get(),rem.get(),nv)).grid(row=4,column=1,padx=2,pady=2)
    
def nouvel_eleve_valider(n, p, num, rem, fen):
    if(n!="" and p!="" and num!="" and rem!=""):
        listeeleves.append(eleve(n,p,"0",num,autre=rem))
        fen.destroy()
        update_listes()
    else:
        showerror(title="Erreur", message="Remplissez toutes les champs !")
        
#----------------------------------------------------------------------------------

#---------------MENU FENETRE PRINCIPALE---------------------------------------------------------------
menubar = Menu(fenetre_principale)

menu1 = Menu(menubar, tearoff=0)
#
#menu1.add_command(label="Effectuer un tri", command=tri)
#menu1.add_command(label="Actualiser", command=update_listes)
#menu1.add_command(label="Editer", command=alert)
#menu1.add_separator()
#menu1.add_command(label="Propriétés", command=edit_var_glob)
#menu1.add_command(label="Quitter", command=fenetre_principale.quit())
#menubar.add_cascade(label="Fichier", menu=menu1)

menusauv = Menu(menubar, tearoff=0)
menusauv.add_command(label="Charger une sauvegarde de saison", command=charger_sauv)
menusauv.add_command(label="Créer une sauvegarde de saison", command=creer_sauv)
menusauv.add_command(label="Récupérer les données d'une nouvelle saison", command=recup)
menusauv.add_separator()
menusauv.add_command(label="Effectuer un tri", command=tri)
menusauv.add_separator()
menusauv.add_command(label="Elèves sans places", command=eleves_sans_rien)
menubar.add_cascade(label="Gestion des données", menu=menusauv)

menu2 = Menu(menubar, tearoff=0)
# menu2.add_command(label="Couper", command=alert)
# menu2.add_command(label="Copier", command=alert)
menu2.add_command(label="Ajouter un élève extérieur", command=nouvel_eleve)
menubar.add_cascade(label="Edition", menu=menu2)
# 
# menu3 = Menu(menubar, tearoff=0)
# menu3.add_command(label="A propos", command=alert)
# menubar.add_cascade(label="Aide", menu=menu3)
menu3 = Menu(menubar, tearoff=0)
menu3.add_command(label="Exporter les fiches spectacles", command=pdf_spectacles)
menu3.add_command(label="Exporter les fiches élèves", command=exporter_fiches_eleves)
menubar.add_cascade(label="Exporter", menu=menu3)

fenetre_principale.config(menu=menubar)
fenetre_principale.title("ClubQ")
fenetre_principale.geometry('{}x{}'.format(400, 550))
#----------------------------------------------------------------------------------

#Clics sur les listes
liste_e.bind("<Double-1>", fiche_eleve)
liste_s.bind("<Double-1>", fiche_spec)

recherche.bind("<Return>",frecherche)

fenetre_principale.mainloop()























