import cv2, sys, numpy, os, time, json

def logare_faciala(time_to_log, log_frame_req, log_framedelay, debug=False):
    haar_file = 'C:\\Users\\cosmi\\Desktop\\hackathon minunat\\Hackathon-2024\\modules\\recognitionhaarcascade_frontalface_default.xml'
    datasets = 'C:\\Users\\cosmi\\Desktop\\hackathon minunat\\Hackathon-2024\\data\\faces'
    
    status_logare = False
    start_time = time.time()
    detected_frames = 1
    
    if debug: print('Initializare model 1/2')

    (images, labels, names, id) = ([], [], {}, 0)
    for (subdirs, dirs, files) in os.walk(datasets):
        for subdir in dirs:
            names[id] = subdir
            subjectpath = os.path.join(datasets, subdir)
            for filename in os.listdir(subjectpath):
                path = subjectpath + '/' + filename
                label = id
                images.append(cv2.imread(path, 0))
                labels.append(int(label))
            id += 1
    (width, height) = (130, 100)

    def frame_debug(img, pt1, pt2, color, thickness, r, d):
        x1,y1 = pt1
        x2,y2 = pt2
    
        cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
        cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
        cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)
    
        cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
        cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
        cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)
        
        cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
        cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
        cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

        cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
        cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
        cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)

    # Crearea unui tablou numpy din listele de imagini si etichete
    (images, labels) = [numpy.array(lists) for lists in [images, labels]]

    # Antrenarea modelului prin algoritmul Local Binary Patterns (LBP)
    model = cv2.face.LBPHFaceRecognizer_create()
    # Antrenare locala a modelului folosind imaginile si etichetele pentru corelarea acestora
    model.train(images, labels)

    face_cascade = cv2.CascadeClassifier(haar_file)
    webcam = cv2.VideoCapture(0)
    if debug: print('Initializare model 2/2')

    # Bucla principala 
    while time.time() - start_time < time_to_log:
        (_, im) = webcam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x,y,w,h) in faces:
            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, (width, height))

            prediction = model.predict(face_resize)
            
            #Afiseaza numele persoanei si probabilitatea de a fi indentificata corect - Functie de debug
            
            if debug: frame_debug(im, (x, y), (x + w, y + h), (0, 255, 255), 2, 15, 30)
            if prediction[1] < 74:
                detected_frames += 1
                if debug: 
                    cv2.putText(im,'%s' % (names[prediction[0]].strip()),(x + 5, (y + 25) + h), cv2.FONT_HERSHEY_PLAIN,1.5,(20,185,20), 2)
                    probability = (prediction[1]) if prediction[1] <= 100.0 else 100.0
                    print("Persoana identificata: {}, probabilitate: {}%".format(names[prediction[0]].strip(), round((probability / 74.5) * 100, 2)))
            else:
                if debug: cv2.putText(im,'Neidentificat',(x + 5, (y + 25) + h), cv2.FONT_HERSHEY_PLAIN,1.5,(65,65, 255), 2)
    
        if detected_frames >= log_frame_req:
            status_logare = True
            webcam.release()
            cv2.destroyAllWindows()
            break
        
        time.sleep(log_framedelay)       
        
    return status_logare