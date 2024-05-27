from ultralytics import YOLO
import cv2
from util import read_license_plate, send_license_plate

results = {}
placa_anterior = None

license_plate_detector = YOLO('ModelitoPlacasBestOptimizado.pt')

# load video
cap = cv2.VideoCapture(0)



# read frames
frame_nmr = -1
ret = True
while ret:
    frame_nmr += 1
    ret, frame = cap.read()
    if ret:
        results[frame_nmr] = {}
        license_plates = license_plate_detector(frame)[0]
        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate

            # crop license plate
            license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]

            # process license plate
            license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
            _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

            # read license plate number
            license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)

            if license_plate_text is not None:
                print(license_plate_text)
                if (license_plate_text != placa_anterior):
                    placa_anterior = license_plate_text
                    resultado =  send_license_plate(license_plate_text)
                    print(resultado)
                # Dibujar caja delimitadora alrededor de la matrícula
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (43, 57, 192), 2)
                text = f"{license_plate_text} Score: {int(license_plate_text_score * 100)}%"
                cv2.putText(frame, text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_DUPLEX, 0.9, (43, 57, 192), 2)
               # Mostrar la transmisión en una ventana
    cv2.imshow('Camara en vivo', frame)

    # Leer el siguiente frame
    ret, frame = cap.read()

    # Salir si se presiona 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()