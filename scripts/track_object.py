#!/usr/bin/env python3
"""Kinematic pass: detect and track the brightest compact object per frame.
Usage: python3 scripts/track_object.py sources/media/CLIP.mp4 [--out spine/tracks.csv] [--min-area 4]

Outputs PIXEL COORDINATES ONLY. Never converts to altitude, distance, or speed:
those require camera intrinsics and range that this corpus does not provide.
Deriving physical velocities from uncalibrated footage is fabrication."""
import argparse, csv, os, sys
import cv2, numpy as np

def track(path, min_area=4, thresh_pct=99.5):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    rid = os.path.splitext(os.path.basename(path))[0]
    rows, frame_no = [], 0
    while True:
        ok, frame = cap.read()
        if not ok: break
        g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        g = cv2.GaussianBlur(g, (5,5), 0)
        t = np.percentile(g, thresh_pct)
        _, mask = cv2.threshold(g, t, 255, cv2.THRESH_BINARY)
        n, lab, stats, cent = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
        best = None
        for i in range(1, n):
            a = stats[i, cv2.CC_STAT_AREA]
            if a < min_area: continue
            w, h = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
            if max(w, h) > min(g.shape) * 0.5: continue   # skip full-frame washes
            if best is None or a > best[1]: best = (i, a)
        if best:
            i = best[0]
            cx, cy = cent[i]
            x, y = stats[i, cv2.CC_STAT_LEFT], stats[i, cv2.CC_STAT_TOP]
            w, h = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
            rows.append([rid, frame_no, round(frame_no/fps, 3), round(float(cx),2), round(float(cy),2),
                         int(stats[i, cv2.CC_STAT_AREA]), round(float(g[lab==i].mean()),2),
                         f"{x},{y},{w},{h}"])
        frame_no += 1
    cap.release()
    return rows, frame_no, fps

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--out", default="spine/tracks.csv")
    ap.add_argument("--min-area", type=int, default=4)
    a = ap.parse_args()
    rows, total, fps = track(a.video, a.min_area)
    new = not os.path.exists(a.out)
    with open(a.out, "a", newline="") as fh:
        w = csv.writer(fh)
        if new: w.writerow(["release_id","frame","t_seconds","cx_px","cy_px","area_px","mean_intensity","bbox"])
        w.writerows(rows)
    print(f"{os.path.basename(a.video)}: {len(rows)} detections across {total} frames at {fps:.2f} fps "
          f"({100*len(rows)/max(total,1):.0f}% frames with a candidate)")
