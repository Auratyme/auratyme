# Auratyme

Auratyme to aplikacja służąca do planowania i zarządzania harmonogramami, wspierana przez sztuczną inteligencję.  
Projekt składa się z dwóch głównych części: backendu (API i logika biznesowa) oraz aplikacji mobilnej.  
Dodatkowo dostępny jest panel analityczny do testowania i generowania harmonogramów przez AI.

## Panel analityczny (ważne — testowanie i demonstracja)

Uwaga: udostępniamy publicznie zahostowany Panel analityczny który:
- analizuje zależności i metryki w wygenerowanych harmonogramach,
- pomaga odkrywać wzorce i zależności,
- wspiera rozwój i optymalizację modeli AI oraz algorytmów planowania poprzez zbieranie metryk i informacji zwrotnych.

---

## Jak uruchomić

### Backend
Instrukcja uruchomienia backendu znajduje się w folderze `backend` w pliku `README.md`.  
Backend projektu jest już zahostowany na serwerze i to właśnie ten backend obsługuje panel analityczny.

**Wymagania:**
- Docker
- Docker Compose
  
### Aplikacja mobilna 
Instrukcja uruchomienia aplikacji mobilnej znajduje się w folderze `mobile-app` w pliku `README.md`.  
Ważne: Frontend na ten moment nie jest jeszcze zintegrowany z backendem. Z tego powodu udostępniony Panel analityczny który stanowi jedyny natychmiastowy sposób na pokazanie jak działa generowanie i analiza harmonogramów.

**Wymagania:**
- Node.js
