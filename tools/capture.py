# -*- coding: utf-8 -*-
"""
피클(Pickle) AI 비서를 위한 초고속 화면 캡처 모듈
- 전체 모니터 화면 캡처
- 전송 속도 최적화를 위한 리사이즈(1280px) 및 JPEG 압축
- 표준 출력(stdout)으로 Base64 청크 스트림 반환
"""
import sys, io, base64, mss
from PIL import Image

def capture_screen():
    # mss 최신/구버전 호환성 지원 (DeprecationWarning 방지)
    sct_cls = getattr(mss, "MSS", mss.mss)
    with sct_cls() as sct:
        mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
        img = Image.frombytes("RGB", sct.grab(mon).size, sct.grab(mon).bgra, "raw", "BGRX")
        
        # 1280px 비율 리사이즈 및 압축
        w, h = img.size
        target_w = 1280
        target_h = int(h * (target_w / w))
        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=65)
        b64_str = base64.b64encode(buf.getvalue()).decode("ascii")
        
        print(f"INFO:{w}x{h}")
        print("===START_SCREEN_CHUNK===")
        for i in range(0, len(b64_str), 200):
            print(b64_str[i:i+200])
        print("===END_SCREEN_CHUNK===")

if __name__ == "__main__":
    capture_screen()
