from pydantic import BaseModel,Field,field_validator
from enum import Enum
from typing import Optional

# ENUMS  
class Origine(str, Enum):
    VENTE = "Vente"
    HERITAGE = "Héritage"
    PARTAGE = "Partage"
    DONATION = "Donation"
    PROMESSE = "Promesse" 

class TypeLot(str, Enum):
    APPARTEMENT="Appartement"
    MAISON = "Maison"
    PARKING = "parking"
    AUTRE= "Autre"

class Civility(str,Enum):
    MR = "Mr"
    MME = "Mme" 
    AUTRE = "Aut"

class MaritalStatus(str,Enum):
    CELIBATAIRE = "Célibataire"
    MARIE = "Marié"
    DIVORCE = "Divorcé"
    VEUF = "Veuf"

class OwnerType(str,Enum):  
    PHYSIQUE = "Physique"
    MORALE = "Morale"

#Sous Classes

class Owner(BaseModel):
    civility: Civility = Field(description="Civilité : Monsieur, Madame ou Mademoiselle")
    first_name: str = Field(description="Prénom de la personne")
    last_name: str = Field(description="Nom de famille de la personne")
    nationality: Optional[str] = Field(None, description="Nationalité de la personne ex: Française")
    profession: Optional[str] = Field(None, description="Profession ou fonction de la personne")
    email: Optional[str] = Field(None, description="Adresse email")
    phone: Optional[str] = Field(None, min_length=10,  description="Numéro de téléphone")
    type: OwnerType = Field(description="Type : Physique pour une personne physique, Morale pour une société")    
    entreprise_name: Optional[str] = Field(None, description="Nom de la société si type est Morale")
    birth_date: Optional[str] = Field(None, description="Date de naissance au format jj/mm/yyyy")
    birth_place: Optional[str] = Field(None, description="Ville et pays de naissance")
    siren: Optional[str] = Field(None, description="Numéro SIREN — obligatoire si type est Morale")
    marital_status: Optional[MaritalStatus] = Field(None, description="Situation maritale : Célibataire, Marié,Mariée Divorcé ou Veuf")
    
    #Validation spécifique pour la situation maritale : accepter différentes variantes et les normaliser en une valeur de l'enum MaritalStatus
    @field_validator("marital_status",mode="before")
    @classmethod
    def marital_status_validator(cls,value):
        if value:
            value = value.strip().upper()
            if value in ["CELIBATAIRE", "CELIB"]:
                return MaritalStatus.CELIBATAIRE
            elif value in ["MARIE", "MARIÉ", "MARIÉE"]:
                return MaritalStatus.MARIE
            elif value in ["DIVORCE", "DIVORCÉ", "DIVORCÉE"]:
                return MaritalStatus.DIVORCE
            elif value in ["VEUF", "VEUVE"]:
                return MaritalStatus.VEUF
        return None

    #Validation conditionnelle : si type est Morale, alors siren est obligatoire
    @field_validator("siren")
    @classmethod
    def siren_validator(cls,value,info):
        if info.data.get("type") == OwnerType.MORALE and not value:
            raise ValueError("Le numéro SIREN est obligatoire pour les personnes morales")
        return value

class Adresse(BaseModel):
    adress: Optional[str] = Field(None, description="Numéro et nom de la rue ex: 32 rue des Lilas")
    city: Optional[str] = Field(None, description="Ville")
    zipcode: Optional[str] = Field(None,description="Code postal à 5 chiffres")

class Lot(BaseModel):
    num_lot: str = Field(description="Numéro du lot dans la copropriété")
    type: TypeLot = Field(description="Type de lot : Appartement, Cave, Parking, etc.")
    floor: Optional[int] = Field(None, description="Étage : RDC=0, sous-sol=-1, 1er étage=1, etc.")
    nbr_rooms: Optional[int] = Field(None, description="Nombre de pièces principales")
    nbr_bedrooms: Optional[int] = Field(None, description="Nombre de chambres")
    nbr_bathrooms: Optional[int] = Field(None, description="Nombre de salles de bain")
    nbr_door: Optional[int] = Field(None, description="Numéro de porte")

class Cadastre(BaseModel):
    prefixe: str = Field(description="Préfixe cadastral, par défaut 000")
    section: str = Field(description="Section cadastrale : 1 ou 2 lettres uniquement ex: AB")
    num_parcelle: int = Field(description="Numéro de parcelle, entier entre 1 et 9999")
    adresse: Optional[str] = Field(None, description="Adresse complète du bien cadastré")

# Main Class
class AttestationVente(BaseModel):
    origin: Origine = Field(description="Origine de la mutation : VENTE, HERITAGE, DONATION, etc.")
    adress: Optional[Adresse] = Field(None, description="Adresse du bien immobilier")
    lots: Optional[list[Lot]] = Field(None, description="Liste des lots de la copropriété")
    cadastres: Optional[list[Cadastre]] = Field(None, description="Références cadastrales du bien")
    nbr_rooms: Optional[int] = Field(None, description="Nombre total de pièces principales")
    nbr_bedrooms: Optional[int] = Field(None, description="Nombre de chambres")
    nbr_bathrooms: Optional[int] = Field(None, description="Nombre de salles de bain")
    surface: Optional[float] = Field(None, description="Surface habitable en m²")
    price: Optional[float] = Field(None, description="Prix de vente en euros, chiffres uniquement")
    description: Optional[str] = Field(None, description="Description générale du bien")
    old_owners: list[Owner] = Field(description="Liste des anciens propriétaires (vendeurs)")
    new_owners: list[Owner] = Field(description="Liste des nouveaux propriétaires (acheteurs)")


