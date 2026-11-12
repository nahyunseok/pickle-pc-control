# -*- coding: utf-8 -*-
"""
피클(Pickle) AI 비서를 위한 마우스 좌표 클릭 모듈
사용법: python click.py <x좌표> <y좌표> [클릭수]
예시: python click.py 960 540 1
"""
import sys, pyautogui

def click_coords():
    if len(sys.argv) < 3:
        print("Usage: python click.py <x> <y> [clicks]")
        sys.exit(1)
        
    x = int(sys.argv[1])
    y = int(sys.argv[2])
    clicks = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    pyautogui.click(x, y, clicks=clicks)
    print(f"CLICKED_SUCCESS:{x},{y},clicks={clicks}")

if __name__ == "__main__":
    click_coords()
