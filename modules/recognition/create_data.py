import cv2, numpy, sys, os, time

def inregistrare_faciala(time_to_reg, req_frame, frame_delay, debug=False):
    current_dir = 'C:\\Users\\cosmi\\Desktop\\hackathon minunat\\Hackathon-2024'

    haar_file = os.path.join(current_dir, 'modules', 'recognition', 'haarcascade_frontalface_default.xml')
    datasets = os.path.join(current_dir, 'data', 'faces')
    sub_dataset = 'Abdullah'
    
    status_inregistrare = False
    
    path = os.path.join(datasets, sub_dataset)

    if not os.path.isdir(path):
        os.makedirs(path)
        
    #Marirea imaginilor
    (width, height) = (130, 100)

    model = cv2.CascadeClassifier(haar_file)

    #ID camera, 0 - intern, 1 - extern
    raspcam = cv2.VideoCapture(0)

    #Contor pentru cadre
    saved_frames = 1
    start_time = time.time()

    #Verificare status camera inainte de initializare
    if debug: print("Initializare 1/2 (Camera) ")
    time.sleep(2)
    if not raspcam.isOpened():
        if debug: print("Initializarea 1/2 a esuat")
        sys.exit()
    else:
        if debug: print("Initializare completa")

    #Bucla principala - cadre camera
    try:
        while (time.time() - start_time) <= time_to_reg and saved_frames <= req_frame:
            ret_val, im = raspcam.read()
            if ret_val:
                gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                
                #Variabile pentru pozitionare si marime ROI, chenar vizual
                h, w = im.shape[:2]
                center = (w // 2, h // 2)
                rect_width, rect_height = 200, 200
                top_left = (center[0] - rect_width // 2, center[1] - rect_height // 2)
                bottom_right = (center[0] + rect_width // 2, center[1] + rect_height // 2)
                
                #Frame vizual pentru a ajuta utilizatorul sa se pozitioneze in zona de captura (in ROI)
                cv2.rectangle(im, top_left, bottom_right, (132, 77, 184), 2)
                
                #Definirea regiunii de interes (ROI)
                roi = gray[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

                #Verificarea prezentei fetei in cadrul ROI
                if roi.size > 0:
                    faces = model.detectMultiScale(roi, 1.3, 4)
                    
                    for (x, y, w, h) in faces:
                        face_x, face_y = top_left[0] + x, top_left[1] + y
                        
                        if debug: cv2.rectangle(im, (face_x, face_y), (face_x + w, face_y + h), (0, 255, 0), 2)
                        
                        #Prelucrare imagine si salvare
                        face = gray[face_y:face_y + h, face_x:face_x + w]
                        face_resize = cv2.resize(face, (width, height))
                        cv2.imwrite('%s/%s.png' % (path, saved_frames), face_resize)
                        
                        saved_frames += 1
            if saved_frames >= req_frame:
                status_inregistrare = True
                break

        cv2.imshow('OpenCV', im)
        
    finally:
        if debug == True: print("Inregistrarea faciala a fost finalizata")
        raspcam.release()
        cv2.destroyAllWindows()
        return status_inregistrare