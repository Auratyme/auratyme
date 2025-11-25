# Auratyme

Auratyme to aplikacja służąca do planowania i zarządzania harmonogramami, wspierana przez sztuczną inteligencję.  
Projekt składa się z dwóch głównych części: backendu (API i logika biznesowa) oraz aplikacji mobilnej.  
Dodatkowo dostępny jest panel do testowania generowania harmonogramów przez AI, co pozwala eksperymentować z tworzeniem planów i zadań w sposób automatyczny.

---

## Jak uruchomić

### Backend
Instrukcja uruchomienia backendu znajduje się w folderze `backend` w pliku `README.md`.  

**Wymagania:**
- Docker
- Docker Compose

### Aplikacja mobilna
Instrukcja uruchomienia aplikacji mobilnej znajduje się w folderze `mobile-app` w pliku `README.md`.  

**Wymagania:**
- Node.js

---

## Panel testowy AI
Backend zawiera panel testowy, który pozwala na generowanie harmonogramów przy użyciu AI.  
Panel umożliwia:
- Testowanie różnych scenariuszy harmonogramów
- Sprawdzanie efektów generowania AI przed integracją z aplikacją mobilną
- Eksperymentowanie z parametrami generacji harmonogramów
