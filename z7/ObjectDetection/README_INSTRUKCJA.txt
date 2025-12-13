ZADANIE 8 - Custom Vision Object Detection
===========================================

STRUKTURA:
---------
ObjectDetection/
  ├── training_images/     (tutaj wklejasz obrazy treningowe + adnotacje XML)
  ├── test_images/         (tutaj wklejasz obrazy testowe)
  ├── train_detection.py   (script do trenowania)
  ├── test_detection.py    (script do testowania)
  └── detection_config.json (konfiguracja projektu)


KROKI:
------

1. PRZYGOTUJ DANE TRENINGOWE (minimum 15-20 obrazów)
   - Umieść obrazy w: training_images/
   - Dla każdego obrazu stwórz plik XML z bounding boxy
   
   Format pliku XML (Pascal VOC):
   
   Plik: training_images/image1.jpg  →  training_images/image1.xml
   
   <annotation>
     <filename>image1.jpg</filename>
     <object>
       <name>osoba</name>
       <bndbox>
         <xmin>100</xmin>
         <ymin>50</ymin>
         <xmax>200</xmax>
         <ymax>300</ymax>
       </bndbox>
     </object>
     <object>
       <name>samochod</name>
       <bndbox>
         <xmin>250</xmin>
         <ymin>150</ymin>
         <xmax>500</xmax>
         <ymax>350</ymax>
       </bndbox>
     </object>
   </annotation>


2. URUCHOM INICJALIZACJĘ PROJEKTU:
   python train_detection.py
   
   To stworzy:
   - Nowy projekt "ObjectDetectionLab8" w Azure
   - Tagi: osoba, samochod, pies, kot
   - Plik detection_config.json


3. UPLOADUJ OBRAZY TRENINGOWE
   python train_detection.py --upload
   

4. TRENUJ MODEL
   python train_detection.py --train
   
   Wynik: Metryka mAP (mean Average Precision)
   - mAP @ 0.5 IOU = Dokładność przy progu 50% pokrycia
   - mAP @ 0.75 IOU = Dokładność przy progu 75% pokrycia
   

5. PRZYGOTUJ OBRAZY TESTOWE
   - Umieść w: test_images/
   - Idealne: zdjęcia z WIELOMA obiektami różnych typów
   - Przykład: zdjęcie z osobą, samochodem i psem
   

6. TESTUJ MODEL
   python test_detection.py
   
   Wyświetli:
   - Liczba wykrytych obiektów
   - Typ obiektu (tag)
   - Confidence dla każdego obiektu
   - Współrzędne bounding box (left, top, width, height)


WSPÓŁRZĘDNE BOUNDING BOX:
------------------------

Format Pascal VOC (xmin, ymin, xmax, ymax):
- Piksele od lewego górnego rogu (0,0)
- xmin = lewa krawędź
- ymin = górna krawędź  
- xmax = prawa krawędź
- ymax = dolna krawędź

Przykład:
Osoba na obrazie 640x480, która zajmuje lewy górny kwadrat 100x100 pikseli:
- xmin=0, ymin=0, xmax=100, ymax=100

Samochód na środku obrazu:
- xmin=200, ymin=150, xmax=450, ymax=350


NARZĘDZIA DO ANOTACJI (opcjonalnie):
-----------------------------------

Jeśli chcesz GUI do rysowania bounding boxów:

1. Labelimg (Python):
   pip install labelimg
   labelimg training_images/

2. CVAT (Online, darmowy):
   https://app.cvat.ai/

3. Makesense.ai (Online, bez rejestracji):
   https://www.makesense.ai/


METRYKI OBJECT DETECTION:
------------------------

mAP (mean Average Precision):
- Średnia precyzja dla wszystkich klas
- Bierze pod uwagę dokładność lokalizacji (bounding box)
- Jest bardziej zaawansowana niż classification metrics

Precision: Ile z wykrytych obiektów to TRUE POSITIVES
Recall: Ile z rzeczywistych obiektów zostało znalezione

IOU (Intersection over Union):
- Miara pokrycia między predicted bbox a ground-truth bbox
- IOU > 0.5 zwykle = prawidłowa detekcja
- IOU > 0.75 = excellent detekcja


OCZEKIWANE WYNIKI:
-----------------

Training:
- mAP @ 0.5: 70-85% (zależy od jakości danych)
- mAP @ 0.75: 50-70%

Validation:
- Powinny być podobne do training (brak overfittingu)
- Jeśli validation < training o >10%: overfit


PRZYDATNE LINKI:
---------------
- Azure Custom Vision Docs: https://learn.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/
- Object Detection Format: https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/python-tutorial-od
- Pascal VOC Format: http://host.robots.ox.ac.uk/pascal/VOC/
