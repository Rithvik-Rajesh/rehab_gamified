import cv2
import mediapipe as mp
import math

class HandTracker:
    """
    A class to track hands using the Mediapipe library and provide utility functions.
    """
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        """
        Initializes the HandTracker.
        :param mode: Whether to treat the input images as a batch or a video stream.
        :param max_hands: Maximum number of hands to detect.
        :param detection_con: Minimum detection confidence.
        :param track_con: Minimum tracking confidence.
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, frame, draw=True):
        """
        Finds hands in a BGR image.
        :param frame: The image to find hands in.
        :param draw: Whether to draw the hand landmarks and connections.
        :return: The image with or without the drawings.
        """
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return frame

    def get_landmark_positions(self, frame, hand_index=0, draw=True):
        """
        Gets the landmark positions for a specific hand.
        :param frame: The image to find landmarks in.
        :param hand_index: The index of the hand to get landmarks for.
        :param draw: Whether to draw circles on the landmarks.
        :return: A list of landmark positions [id, x, y].
        """
        lm_list = []
        if self.results and self.results.multi_hand_landmarks:
            if hand_index < len(self.results.multi_hand_landmarks):
                hand = self.results.multi_hand_landmarks[hand_index]
                for id, lm in enumerate(hand.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
                    if draw:
                        cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return lm_list

    def calculate_distance(self, p1, p2):
        """
        Calculates the Euclidean distance between two points.
        :param p1: The first point [id, x, y].
        :param p2: The second point [id, x, y].
        :return: The distance between the points.
        """
        x1, y1 = p1[1], p1[2]
        x2, y2 = p2[1], p2[2]
        return math.hypot(x2 - x1, y2 - y1)

    def calculate_angle(self, p1, p2, p3):
        """
        Calculates the angle between three points, with p2 as the vertex.
        :param p1: The first point [id, x, y].
        :param p2: The second point (vertex) [id, x, y].
        :param p3: The third point [id, x, y].
        :return: The angle in degrees.
        """
        x1, y1 = p1[1], p1[2]
        x2, y2 = p2[1], p2[2]
        x3, y3 = p3[1], p3[2]

        # Calculate the angle using atan2
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360
        
        # Ensure the angle is between 0 and 180
        if angle > 180:
            angle = 360 - angle
            
        return angle

    def get_pinch_gesture(self, lm_list, pinch_threshold=30):
        """
        Detects a pinch gesture and returns the status and position.
        :param lm_list: The list of landmark positions.
        :param pinch_threshold: The distance threshold to consider a pinch.
        :return: A tuple (is_pinching, pinch_position).
        """
        if len(lm_list) >= 9:
            thumb_tip = lm_list[4]
            index_tip = lm_list[8]
            
            distance = self.calculate_distance(thumb_tip, index_tip)
            
            # Calculate the midpoint for the cursor position
            pinch_x = (thumb_tip[1] + index_tip[1]) // 2
            pinch_y = (thumb_tip[2] + index_tip[2]) // 2
            
            if distance < pinch_threshold:
                return True, (pinch_x, pinch_y)
        
        return False, None

