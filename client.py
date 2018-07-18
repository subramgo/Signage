"""
Mock up a video feed pipeline
"""
import asyncio
import logging
import sys
import cv2
import dlib


logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('async')
logger.setLevel(logging.INFO)

host="root:pass@192.168.1.4"
stream = "ufirststream"

sem = asyncio.Semaphore(15)
detector = dlib.get_frontal_face_detector()
cap = cv2.VideoCapture('rtsp://'+host+'/'+stream)

async def process_video():
    tasks = list()
    frame_ind = 0
    while 1:
        ret, frame = cap.read()
        await sem.acquire()
        if not ret:
            break
        tasks.append(asyncio.ensure_future(process_frame(frame, frame_ind)))
        frame_ind += 1
        await asyncio.sleep(0)
    await asyncio.gather(tasks)


async def process_frame(frame, frame_ind):
    logger.info("Processing frame {}".format(frame_ind))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dets, scores, idx = detector.run(frame, 1, -1)
    windows = []
    people_count = 0
    logger.info("No faces detected {}".format(len(dets)))
    if len(dets) > 0:
        for i, d in enumerate(dets):
            people_count+=1
            windows.append([d.left(), d.top(), d.right(), d.bottom()])

    logger.info(str(people_count) + ",".join(str(r) for v in windows for r in v))
    logger.info("Finished processing frame {}".format(frame_ind))
    sem.release()

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_video())
    logger.info("Completed")

if __name__ == '__main__':
    main()