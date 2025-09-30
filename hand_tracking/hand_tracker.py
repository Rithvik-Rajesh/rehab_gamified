import cv2
import mediapipe as mp
import math

class HandTracker:
    def __init__(self, max_hands=2, detection_con=0.5, track_con=0.5):
        self.hands = mp.solutions.hands.Hands(max_num_hands=max_hands,
                                              min_detection_confidence=detection_con,
                                              min_tracking_confidence=track_con)
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None
        self.cap = cv2.VideoCapture(0)

    def find_hands(self, frame, draw=True):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(frame_rgb)

        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
        return frame

    def get_landmark_positions(self, frame, hand_index=0):
        landmark_list = []
        if self.results and self.results.multi_hand_landmarks:
            if hand_index < len(self.results.multi_hand_landmarks):
                hand = self.results.multi_hand_landmarks[hand_index]
                for id, lm in enumerate(hand.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmark_list.append([id, cx, cy])
        return landmark_list

    def calculate_distance(self, p1, p2):
        # p1 and p2 are tuples (x, y)
        return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

    def calculate_angle(self, p1, p2, p3):
        # p1, p2, p3 are tuples (x, y)
        # Angle at p2
        ang = math.degrees(math.atan2(p3[1] - p2[1], p3[0] - p2[0]) -
                           math.atan2(p1[1] - p2[1], p1[0] - p2[0]))
        return ang + 360 if ang < 0 else ang

    def release_camera(self):
        self.cap.release()