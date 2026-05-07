import flet as ft
import asyncio

def task_controls(count=0):
    if len(asyncio.all_tasks()) >= 1:
        try:
            print("\n" * count + f"{'===='*30}\n 🪄 Background Task Controls\n{'===='*30}")
            for i, task in enumerate(asyncio.all_tasks()):
                print(f" [{i}] 이름: {task.get_name():<8}| 상태: {task._state} | 코루틴: {task.get_coro()}")
            print(f"{'===='*30}")
        except: pass
    else: print("\n" * 30)

def views_controls(page: ft.Page, count=0):
    print("\n" * count + f" 🪄 View List\n{'===='*30}")
    for i, view in enumerate(page.views):
        v_route = view.route
        v_controls_count = len(view.controls)
        v_appbar = "Yes" if view.bottom_appbar else "No"
        print(f" [{i:>2}] 경로(Route): {v_route:<30} | 컨트롤 수: {v_controls_count:>4} | Bottom AppBar: {v_appbar}")
    print(f"{'===='*30}")