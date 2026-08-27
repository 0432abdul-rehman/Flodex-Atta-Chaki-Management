from pathlib import Path
from typing import List, Optional


class FaceMatcher:
    """Optional face/photo matching helper.

    If OpenCV is available, detects whether a face is present in an input image and
    returns best filename-level match with known customer photo paths.
    """

    def __init__(self) -> None:
        self.cv2 = None
        try:
            import cv2

            self.cv2 = cv2
        except Exception:
            self.cv2 = None

    @property
    def supported(self) -> bool:
        return self.cv2 is not None

    def image_has_face(self, image_path: str) -> bool:
        if not self.supported:
            return False
        frame = self.cv2.imread(image_path)
        if frame is None:
            return False
        gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
        cascade = self.cv2.CascadeClassifier(self.cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
        return len(faces) > 0

    def guess_match(self, image_path: str, known_photo_paths: List[str]) -> Optional[str]:
        if not self.image_has_face(image_path):
            return None

        source_stem = Path(image_path).stem.lower()
        for photo in known_photo_paths:
            if not photo:
                continue
            stem = Path(photo).stem.lower()
            if stem == source_stem or source_stem in stem or stem in source_stem:
                return photo
        return None
