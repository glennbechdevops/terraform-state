# Øvelse: Terraform-konfigurasjon med AWS S3, Providers, og State Management

## Mål

I denne øvelsen vil du lære hvordan du konfigurerer Terraform, inkludert både provider og backend.

Som et eksempel finner du også i dette repoet Terraform-kode som oppretter en AWS Lambda-funksjon. Denne Lambda-funksjonen
kaller på AWS-tjenesten Comprehend for å analysere tekst. Vi vil også bruke AWS S3 for å lagre Terraform state-filen.

## AWS Comprehend

AWS Comprehend er en språkforståelsestjeneste som bruker
maskinlæring for å avdekke innsikt og relasjoner i tekst.

Tjenesten kan automatisk analysere tekst for å identifisere
sentiment, nøkkelbegreper, språk, emner og entiteter som navn,
steder eller organisasjoner, noe som gjør den nyttig for alt fra
kundeserviceanalyse til innholdsklassifisering og tekstforståelse.
Here’s a QA pass with some corrections and adjustments to the text to improve clarity and accuracy:

---

### Del 1: Kloning av repository og oppsett av Cloud9

#### Åpne ditt AWS Cloud9-miljø

* Start med å logge inn i AWS Cloud9.
* Lag en klone av dette repositoryet.

#### Deaktiver standardrettigheter i Cloud9

Cloud9 kommer med et sett av standardrettigheter som er tilstrekkelige for mange bruksscenarioer.
Men Cloud9 kan ikke opprette IAM-roller. I denne laben må vi derfor deaktivere **Cloud9 Managed temporary credentials**.

Trykk på "9"-ikonet øverst til høyre, og velg "Preferences". Deaktiver `AWS Managed temporary credentials`.

![Slå av midlertidige Cloud9-credentials](./img/disable_credentials.png)

Deretter må vi lagre egne IAM-nøkler, som vi har gjort i tidligere øvinger.
I Cloud9 terminalen bruker vi kommandoen:

```bash
aws configure
```

* Bruk `eu-west-1` som region.
* Bruk `json` som output format.

### Installer Terraform   
   Hvis Terraform ikke allerede er installert i ditt Cloud9-miljø, installer det ved å følge instruksjonene fra forrige
   del.

```shell
wget https://releases.hashicorp.com/terraform/1.9.0/terraform_1.9.0_linux_amd64.zip
unzip terraform_1.9.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/ 
terraform -v
```

## Konfigruasjon av provider

1. **Required Providers og provider-versjonering**

   Start med å opprette en fil som heter `provider.tf` i ditt prosjekt. Denne filen definerer Terraform-konfigurasjonen
   din, inkludert hvilken provider som skal brukes, og spesifiserer providerens versjon.

```hcl
terraform {
  required_version = ">= 1..0"  # Krever minst versjon 1.6.0 av Terraform
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0" # Bruker AWS-provider versjon 4.x
    }
  }
}

provider "aws" {
  region = "eu-west-1"  # Velg ønsket region
}
```

**Forklaring:**

- `required_version` definierer hvilken versjon av Terraform som er nødvendig
- `required_providers` definerer hvilke providere Terraform trenger for å kjøre konfigurasjonen. I dette tilfellet
  bruker vi `aws`-provider fra HashiCorp.
- `version = "~> 4.0"` sørger for at Terraform bruker versjon 4.x av AWS-provideren, men vil tillate oppdateringer
  innenfor denne store versjonen (altså opp til, men ikke inkludert, 5.0). Dette sikrer stabilitet i konfigurasjonen.

### Oppgaver

* forsøke å endre `required_version` for terraform til en nyere versjon en du installerte i cloud9 og forsøk å gjøre
  en ````terraform init```` hva skjer? Endre tilbake
* Kjør ` terraform apply --auto-approve --var "prefix=<studentnavn>"` -- legg merke til at du får en terraform.tfstate fil i katalogen din, forsikre
  deg om at du vet hvorfor. Spør gjerne ChatGPT :-)
* Vær sikker på at du forstår --var argumentet!

Du kan teste lambdafunksjonen med følgende kommand

```shell
$URL=<output fra terraform, verdien til `Terraform Function` sin URL
curl -X POST $URL -H "Content-Type: application/json" -d '{"text": "I am happy as a camper"}'

```

### Rydd opp

* Kjør `terraform destroy --auto-approve` - hva skjer med `terraform.tfstate` filen din? Hvorfor?

### Del 3: Bruk S3 som backend for Terraform state

1. **Konfigurer S3 som backend for Terraform state**

Legg til følgende konfigurasjon inn `terraform {}` blokken i `provider.tf`

   ```hcl
     backend "s3" {
  bucket = "pgr301-terraform-state-2024"
  key    = "<studentnavn>-state-lab.tfstate"
  region = "eu-west-1"
}
   ```

**Forklaring:**

- `backend "s3"` konfigurerer Terraform til å bruke S3 som backend for state-filen.
- `bucket` refererer til navnet på S3-bucketen som skal lagre state-filen.
- `key` spesifiserer stien til state-filen i S3-bucketen. Dette er filnavnet Terraform bruker for å lagre tilstanden (
  bytt ut `<studentnavn>`).
- `region` spesifiserer hvilken AWS-region som brukes for S3-bucketen.


3. **Initialiser Terraform**

   For at ikke tidligere terraform konfigurasjon blir med videre, kjøre følgende kommandoer for å rydde opp
   ```
      rm -rf .terraform 
      rm *.tfstate
   ```

7. For å sette opp Terraform til å bruke den definerte S3-backenden, kjører du følgende kommando:

   ```bash
   terraform init
   ```

4. **Provisjoner AWS Lambdafunksjonen på nytt **

   Etter å ha initialisert Terraform, kan du kjøre planleggings- og provisjoneringsprosessen for å opprette S3-bucketen:

   ```bash
   terraform plan
   terraform apply --auto-approve
   ```

   **Forklaring:**

- `terraform plan` viser deg hva som kommer til å bli opprettet eller endret i AWS.
- `terraform apply` vil faktisk opprette de definerte ressursene, inkludert S3-bucketen.

5. **Sjekk state-filen i S3**

   Når provisjoneringen er ferdig, kan du gå til AWS-konsollen, finne S3-bucketen du har satt opp som backend, og
   bekrefte at `terraform.tfstate`-filen er opprettet.

### Del 4: Rydd opp

Når du er ferdig med øvelsen, er det viktig å rydde opp ressursene for å unngå unødvendige kostnader. Du kan slette
ressursene ved å kjøre:

```bash
terraform destroy --auto-approve
```

### Oppsummering

I denne øvelsen har du lært hvordan du konfigurerer Terraform med `required_providers`, hvordan du bruker versjonering
av providere for å sikre stabilitet, hvordan du provisjonerer en S3-bucket, og hvordan du bruker S3 som backend for
Terraform state-filer. Du har nå en bedre forståelse av hvordan Terraform håndterer infrastruktur som kode på en sikker
og skalerbar måte.