#include <Windows.h>
#include <iostream>
#include <thread>
#include <atomic>
#include <vector>

// 全局变量控制程序运行
std::atomic<bool> isRunning(true);

// 存储屏幕信息的结构体
struct MonitorInfo
{
    int left;
    int top;
    int right;
    int bottom;
};

// 获取所有屏幕信息
std::vector<MonitorInfo> getMonitorInfos()
{
    std::vector<MonitorInfo> monitors;

    EnumDisplayMonitors(NULL, NULL, [](HMONITOR hMonitor, HDC hdcMonitor, LPRECT lprcMonitor, LPARAM dwData) -> BOOL
                        {
        std::vector<MonitorInfo>* pMonitors = reinterpret_cast<std::vector<MonitorInfo>*>(dwData);
        MonitorInfo info;
        info.left = lprcMonitor->left;
        info.top = lprcMonitor->top;
        info.right = lprcMonitor->right;
        info.bottom = lprcMonitor->bottom;
        pMonitors->push_back(info);
        return TRUE; }, reinterpret_cast<LPARAM>(&monitors));

    return monitors;
}

// 检查坐标是否在任何屏幕范围内
bool isPointOnAnyMonitor(int x, int y, const std::vector<MonitorInfo> &monitors)
{
    for (const auto &monitor : monitors)
    {
        if (x >= monitor.left && x < monitor.right &&
            y >= monitor.top && y < monitor.bottom)
        {
            return true;
        }
    }
    return false;
}

// 键盘事件处理（ESC退出）
void handleKeyboardInput()
{
    while (isRunning)
    {
        if (GetAsyncKeyState(VK_ESCAPE) & 0x8000)
        {
            isRunning = false;
        }
        Sleep(100);
    }
}

// 鼠标点击操作（替换为更推荐的SendInput API，兼容性更好）
void mouseClick(int x, int y)
{
    // 保存当前鼠标位置
    POINT currentPos;
    GetCursorPos(&currentPos);

    // 移动到目标位置
    SetCursorPos(x, y);

    // 使用SendInput（替代过时的mouse_event）模拟左键单击
    INPUT input[2] = {0};
    // 左键按下
    input[0].type = INPUT_MOUSE;
    input[0].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
    // 左键抬起
    input[1].type = INPUT_MOUSE;
    input[1].mi.dwFlags = MOUSEEVENTF_LEFTUP;

    SendInput(2, input, sizeof(INPUT));
    Sleep(50);

    // 恢复原位置
    SetCursorPos(currentPos.x, currentPos.y);
}

// 自动点击线程
void autoClickThread(int x, int y, int intervalSeconds)
{
    while (isRunning)
    {
        // 等待指定时间（可被ESC中断）
        for (int i = 0; i < intervalSeconds * 10 && isRunning; ++i)
        {
            Sleep(100);
        }

        if (isRunning)
        {
            mouseClick(x, y);
            // 仅打印点击坐标和时间
            SYSTEMTIME st;
            GetLocalTime(&st);
            printf("坐标(%d, %d) 单击 - %02d:%02d:%02d\n",
                   x, y, st.wHour, st.wMinute, st.wSecond);
        }
    }
}

int main()
{
    // 设置控制台编码为UTF-8，避免中文乱码
    SetConsoleOutputCP(CP_UTF8);

    // 目标参数（保持坐标不变）
    const int targetX = 931;
    const int targetY = 140;
    const int interval = 30; // 点击间隔（秒）

    // 获取屏幕信息并输出，明确当前屏幕数量
    std::vector<MonitorInfo> monitors = getMonitorInfos();
    std::cout << "检测到屏幕数量：" << monitors.size() << " 块" << std::endl;
    if (monitors.size() > 0)
    {
        std::cout << "当前屏幕分辨率范围：(" << monitors[0].left << "," << monitors[0].top
                  << ") 到 (" << monitors[0].right << "," << monitors[0].bottom << ")" << std::endl;
    }

    // 检查坐标有效性
    if (!isPointOnAnyMonitor(targetX, targetY, monitors))
    {
        std::cerr << "错误：目标坐标(" << targetX << "," << targetY << ")超出屏幕范围" << std::endl;
        return 1;
    }
    std::cout << "目标坐标(" << targetX << "," << targetY << ")有效，程序开始运行（按ESC退出）..." << std::endl;

    // 启动线程
    std::thread inputThread(handleKeyboardInput);
    std::thread clickThread(autoClickThread, targetX, targetY, interval);

    // 等待线程结束
    inputThread.join();
    clickThread.join();

    std::cout << "程序已退出" << std::endl;
    return 0;
}