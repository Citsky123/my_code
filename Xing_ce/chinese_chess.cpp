#include <windows.h>
#include <iostream>
#include <vector>
#include <string>
#include <cstdio>
#include <conio.h>

using namespace std;

// 棋子类型枚举
enum PieceType
{
    NONE,       // 空
    R_GENERAL,  // 红帅
    R_ADVISOR,  // 红士
    R_ELEPHANT, // 红相
    R_HORSE,    // 红马
    R_CHARIOT,  // 红车
    R_CANNON,   // 红炮
    R_SOLDIER,  // 红兵
    B_GENERAL,  // 黑将
    B_ADVISOR,  // 黑士
    B_ELEPHANT, // 黑象
    B_HORSE,    // 黑马
    B_CHARIOT,  // 黑车
    B_CANNON,   // 黑炮
    B_SOLDIER   // 黑卒
};

// 玩家枚举
enum Player
{
    RED,
    BLACK
};

// 棋子类
class Piece
{
private:
    PieceType type;
    int x, y; // 位置坐标
    bool alive;

public:
    Piece(PieceType t, int xPos, int yPos) : type(t), x(xPos), y(yPos), alive(true) {}

    PieceType getType() const { return type; }
    int getX() const { return x; }
    int getY() const { return y; }
    bool isAlive() const { return alive; }
    Player getPlayer() const
    {
        if (type >= R_GENERAL && type <= R_SOLDIER)
            return RED;
        if (type >= B_GENERAL && type <= B_SOLDIER)
            return BLACK;
        return RED; // 不会执行到这里
    }

    void setPosition(int xPos, int yPos)
    {
        x = xPos;
        y = yPos;
    }
    void setAlive(bool a) { alive = a; }

    // 获取棋子的显示字符
    char getChar() const
    {
        switch (type)
        {
        case R_GENERAL:
            return '帅';
        case R_ADVISOR:
            return '仕';
        case R_ELEPHANT:
            return '相';
        case R_HORSE:
            return '马';
        case R_CHARIOT:
            return '车';
        case R_CANNON:
            return '炮';
        case R_SOLDIER:
            return '兵';
        case B_GENERAL:
            return '将';
        case B_ADVISOR:
            return '士';
        case B_ELEPHANT:
            return '象';
        case B_HORSE:
            return '马';
        case B_CHARIOT:
            return '车';
        case B_CANNON:
            return '炮';
        case B_SOLDIER:
            return '卒';
        default:
            return ' ';
        }
    }
};

// 棋盘类
class Board
{
private:
    vector<Piece> pieces;
    int selectedX, selectedY; // 选中的棋子位置
    bool hasSelected;         // 是否有选中的棋子

public:
    Board() : hasSelected(false)
    {
        // 初始化红方棋子
        pieces.emplace_back(R_GENERAL, 4, 9);
        pieces.emplace_back(R_ADVISOR, 3, 9);
        pieces.emplace_back(R_ADVISOR, 5, 9);
        pieces.emplace_back(R_ELEPHANT, 2, 9);
        pieces.emplace_back(R_ELEPHANT, 6, 9);
        pieces.emplace_back(R_HORSE, 1, 9);
        pieces.emplace_back(R_HORSE, 7, 9);
        pieces.emplace_back(R_CHARIOT, 0, 9);
        pieces.emplace_back(R_CHARIOT, 8, 9);
        pieces.emplace_back(R_CANNON, 1, 7);
        pieces.emplace_back(R_CANNON, 7, 7);
        pieces.emplace_back(R_SOLDIER, 0, 6);
        pieces.emplace_back(R_SOLDIER, 2, 6);
        pieces.emplace_back(R_SOLDIER, 4, 6);
        pieces.emplace_back(R_SOLDIER, 6, 6);
        pieces.emplace_back(R_SOLDIER, 8, 6);

        // 初始化黑方棋子
        pieces.emplace_back(B_GENERAL, 4, 0);
        pieces.emplace_back(B_ADVISOR, 3, 0);
        pieces.emplace_back(B_ADVISOR, 5, 0);
        pieces.emplace_back(B_ELEPHANT, 2, 0);
        pieces.emplace_back(B_ELEPHANT, 6, 0);
        pieces.emplace_back(B_HORSE, 1, 0);
        pieces.emplace_back(B_HORSE, 7, 0);
        pieces.emplace_back(B_CHARIOT, 0, 0);
        pieces.emplace_back(B_CHARIOT, 8, 0);
        pieces.emplace_back(B_CANNON, 1, 2);
        pieces.emplace_back(B_CANNON, 7, 2);
        pieces.emplace_back(B_SOLDIER, 0, 3);
        pieces.emplace_back(B_SOLDIER, 2, 3);
        pieces.emplace_back(B_SOLDIER, 4, 3);
        pieces.emplace_back(B_SOLDIER, 6, 3);
        pieces.emplace_back(B_SOLDIER, 8, 3);
    }

    // 查找指定位置的棋子
    Piece *getPieceAt(int x, int y)
    {
        for (auto &piece : pieces)
        {
            if (piece.isAlive() && piece.getX() == x && piece.getY() == y)
            {
                return &piece;
            }
        }
        return nullptr;
    }

    // 检查移动是否合法
    bool isValidMove(int fromX, int fromY, int toX, int toY, Player currentPlayer)
    {
        // 检查是否在棋盘范围内
        if (toX < 0 || toX > 8 || toY < 0 || toY > 9)
        {
            return false;
        }

        Piece *fromPiece = getPieceAt(fromX, fromY);
        Piece *toPiece = getPieceAt(toX, toY);

        // 检查目标位置是否有己方棋子
        if (toPiece && toPiece->getPlayer() == currentPlayer)
        {
            return false;
        }

        // 根据不同棋子类型检查移动规则
        switch (fromPiece->getType())
        {
        case R_GENERAL:
        case B_GENERAL:
            return isValidGeneralMove(fromX, fromY, toX, toY, fromPiece->getType());
        case R_ADVISOR:
        case B_ADVISOR:
            return isValidAdvisorMove(fromX, fromY, toX, toY, fromPiece->getType());
        case R_ELEPHANT:
        case B_ELEPHANT:
            return isValidElephantMove(fromX, fromY, toX, toY, fromPiece->getType());
        case R_HORSE:
        case B_HORSE:
            return isValidHorseMove(fromX, fromY, toX, toY);
        case R_CHARIOT:
        case B_CHARIOT:
            return isValidChariotMove(fromX, fromY, toX, toY);
        case R_CANNON:
        case B_CANNON:
            return isValidCannonMove(fromX, fromY, toX, toY);
        case R_SOLDIER:
        case B_SOLDIER:
            return isValidSoldierMove(fromX, fromY, toX, toY, fromPiece->getType());
        default:
            return false;
        }
    }

    // 移动棋子
    bool movePiece(int fromX, int fromY, int toX, int toY, Player currentPlayer)
    {
        if (!isValidMove(fromX, fromY, toX, toY, currentPlayer))
        {
            return false;
        }

        Piece *fromPiece = getPieceAt(fromX, fromY);
        Piece *toPiece = getPieceAt(toX, toY);

        // 吃掉对方棋子
        if (toPiece)
        {
            toPiece->setAlive(false);
        }

        // 移动棋子
        fromPiece->setPosition(toX, toY);

        return true;
    }

    // 检查将/帅是否被吃掉
    bool isGeneralCaptured(Player player)
    {
        PieceType generalType = (player == RED) ? R_GENERAL : B_GENERAL;
        for (const auto &piece : pieces)
        {
            if (piece.getType() == generalType && piece.isAlive())
            {
                return false;
            }
        }
        return true;
    }

    // 绘制棋盘
    void draw()
    {
        system("cls"); // 清屏

        // 打印列标
        cout << "  ";
        for (int x = 0; x < 9; x++)
        {
            cout << "  " << x << " ";
        }
        cout << endl;

        // 打印棋盘和棋子
        for (int y = 0; y < 10; y++)
        {
            cout << y << " ";
            for (int x = 0; x < 9; x++)
            {
                // 绘制棋盘线条
                cout << "┼";
                if (y == 4 || y == 5)
                {
                    cout << "──"; // 楚河汉界
                }
                else
                {
                    cout << "  ";
                }

                // 检查是否有棋子
                Piece *piece = getPieceAt(x, y);
                if (piece)
                {
                    // 显示棋子，红方用红色，黑方用白色
                    if (piece->getPlayer() == RED)
                    {
                        printf("\033[31m%c\033[0m", piece->getChar()); // 红色
                    }
                    else
                    {
                        printf("%c", piece->getChar()); // 白色
                    }
                }
                else
                {
                    cout << " ";
                }
            }
            cout << "┼" << endl;
        }

        // 打印操作提示
        cout << endl;
        cout << "操作说明: 方向键移动光标, 空格键选择/移动棋子, ESC键退出游戏" << endl;
        cout << "当前轮到" << (currentPlayer == RED ? "\033[31m红方\033[0m" : "黑方") << "走棋" << endl;
    }

    // 处理用户输入
    bool handleInput(int &x, int &y, Player currentPlayer)
    {
        int key = _getch();

        // 方向键处理
        if (key == 224)
        { // 方向键前缀
            key = _getch();
            switch (key)
            {
            case 72:
                if (y > 0)
                    y--;
                break; // 上
            case 80:
                if (y < 9)
                    y++;
                break; // 下
            case 75:
                if (x > 0)
                    x--;
                break; // 左
            case 77:
                if (x < 8)
                    x++;
                break; // 右
            }
            return false;
        }
        // 空格键处理选择/移动
        else if (key == 32)
        {
            if (!hasSelected)
            {
                // 选择棋子
                Piece *piece = getPieceAt(x, y);
                if (piece && piece->getPlayer() == currentPlayer)
                {
                    selectedX = x;
                    selectedY = y;
                    hasSelected = true;
                }
            }
            else
            {
                // 移动棋子
                if (movePiece(selectedX, selectedY, x, y, currentPlayer))
                {
                    hasSelected = false;
                    return true; // 移动成功，切换玩家
                }
                // 如果点击了自己的另一个棋子，则重新选择
                Piece *piece = getPieceAt(x, y);
                if (piece && piece->getPlayer() == currentPlayer)
                {
                    selectedX = x;
                    selectedY = y;
                }
                else
                {
                    hasSelected = false; // 取消选择
                }
            }
        }
        // ESC键退出
        else if (key == 27)
        {
            exit(0);
        }

        return false;
    }

    // 当前玩家（静态成员，方便在draw()中访问）
    static Player currentPlayer;

private:
    // 检查将/帅的移动是否合法
    bool isValidGeneralMove(int fromX, int fromY, int toX, int toY, PieceType type)
    {
        // 将帅不能见面（中间没有棋子）
        if ((type == R_GENERAL && getPieceAt(toX, toY) && getPieceAt(toX, toY)->getType() == B_GENERAL) ||
            (type == B_GENERAL && getPieceAt(toX, toY) && getPieceAt(toX, toY)->getType() == R_GENERAL))
        {
            if (fromX == toX)
            { // 同一列
                bool hasObstacle = false;
                int startY = min(fromY, toY) + 1;
                int endY = max(fromY, toY);
                for (int y = startY; y < endY; y++)
                {
                    if (getPieceAt(fromX, y))
                    {
                        hasObstacle = true;
                        break;
                    }
                }
                if (!hasObstacle)
                {
                    return true; // 可以吃对方将/帅
                }
            }
        }

        // 将帅只能在九宫格内移动
        if (type == R_GENERAL)
        { // 红帅九宫
            if (toX < 3 || toX > 5 || toY < 7 || toY > 9)
            {
                return false;
            }
        }
        else
        { // 黑将九宫
            if (toX < 3 || toX > 5 || toY < 0 || toY > 2)
            {
                return false;
            }
        }

        // 将帅只能上下左右移动一格
        int dx = abs(fromX - toX);
        int dy = abs(fromY - toY);
        return (dx + dy == 1);
    }

    // 检查士/仕的移动是否合法
    bool isValidAdvisorMove(int fromX, int fromY, int toX, int toY, PieceType type)
    {
        // 士/仕只能在九宫格内移动
        if (type == R_ADVISOR)
        { // 红仕九宫
            if (toX < 3 || toX > 5 || toY < 7 || toY > 9)
            {
                return false;
            }
        }
        else
        { // 黑士九宫
            if (toX < 3 || toX > 5 || toY < 0 || toY > 2)
            {
                return false;
            }
        }

        // 士/仕只能斜着走一格
        int dx = abs(fromX - toX);
        int dy = abs(fromY - toY);
        return (dx == 1 && dy == 1);
    }

    // 检查象/相的移动是否合法
    bool isValidElephantMove(int fromX, int fromY, int toX, int toY, PieceType type)
    {
        // 象/相不能过河
        if (type == R_ELEPHANT && toY < 5)
        { // 红相不能过河
            return false;
        }
        if (type == B_ELEPHANT && toY > 4)
        { // 黑象不能过河
            return false;
        }

        // 象/相走田字格
        int dx = abs(fromX - toX);
        int dy = abs(fromY - toY);
        if (dx != 2 || dy != 2)
        {
            return false;
        }

        // 检查象眼是否被塞住
        int eyeX = fromX + (toX - fromX) / 2;
        int eyeY = fromY + (toY - fromY) / 2;
        return (getPieceAt(eyeX, eyeY) == nullptr);
    }

    // 检查马的移动是否合法
    bool isValidHorseMove(int fromX, int fromY, int toX, int toY)
    {
        int dx = abs(fromX - toX);
        int dy = abs(fromY - toY);

        // 马走日字
        if (!((dx == 1 && dy == 2) || (dx == 2 && dy == 1)))
        {
            return false;
        }

        // 检查马腿是否被绊住
        if (dx == 2)
        {
            int legX = fromX + (toX - fromX) / 2;
            if (getPieceAt(legX, fromY) != nullptr)
            {
                return false;
            }
        }
        else
        {
            int legY = fromY + (toY - fromY) / 2;
            if (getPieceAt(fromX, legY) != nullptr)
            {
                return false;
            }
        }

        return true;
    }

    // 检查车的移动是否合法
    bool isValidChariotMove(int fromX, int fromY, int toX, int toY)
    {
        // 车只能直线移动
        if (fromX != toX && fromY != toY)
        {
            return false;
        }

        // 检查路径上是否有障碍物
        if (fromX == toX)
        { // 水平移动
            int startY = min(fromY, toY) + 1;
            int endY = max(fromY, toY);
            for (int y = startY; y < endY; y++)
            {
                if (getPieceAt(fromX, y) != nullptr)
                {
                    return false;
                }
            }
        }
        else
        { // 垂直移动
            int startX = min(fromX, toX) + 1;
            int endX = max(fromX, toX);
            for (int x = startX; x < endX; x++)
            {
                if (getPieceAt(x, fromY) != nullptr)
                {
                    return false;
                }
            }
        }

        return true;
    }

    // 检查炮的移动是否合法
    bool isValidCannonMove(int fromX, int fromY, int toX, int toY)
    {
        // 炮只能直线移动
        if (fromX != toX && fromY != toY)
        {
            return false;
        }

        // 计算路径上的棋子数量
        int obstacleCount = 0;
        if (fromX == toX)
        { // 水平移动
            int startY = min(fromY, toY) + 1;
            int endY = max(fromY, toY);
            for (int y = startY; y < endY; y++)
            {
                if (getPieceAt(fromX, y) != nullptr)
                {
                    obstacleCount++;
                }
            }
        }
        else
        { // 垂直移动
            int startX = min(fromX, toX) + 1;
            int endX = max(fromX, toX);
            for (int x = startX; x < endX; x++)
            {
                if (getPieceAt(x, fromY) != nullptr)
                {
                    obstacleCount++;
                }
            }
        }

        // 炮翻山吃子需要恰好一个障碍物，移动不需要障碍物
        Piece *targetPiece = getPieceAt(toX, toY);
        if (targetPiece)
        {
            return (obstacleCount == 1); // 吃子需要一个炮架
        }
        else
        {
            return (obstacleCount == 0); // 移动不能有障碍物
        }
    }

    // 检查兵/卒的移动是否合法
    bool isValidSoldierMove(int fromX, int fromY, int toX, int toY, PieceType type)
    {
        int dx = abs(fromX - toX);
        int dy = abs(fromY - toY);

        // 兵/卒只能走一格
        if (dx + dy != 1)
        {
            return false;
        }

        // 兵/卒过河前后的移动规则
        if (type == R_SOLDIER)
        {
            // 红兵未过河（y > 4）只能向上移动
            if (fromY > 4 && toY >= fromY)
            {
                return false;
            }
            // 红兵过河后（y <= 4）可以左右移动
            if (fromY <= 4 && dx == 1 && dy == 0)
            {
                return true;
            }
            // 红兵任何时候都不能向下移动
            if (toY > fromY)
            {
                return false;
            }
        }
        else
        { // B_SOLDIER
            // 黑卒未过河（y < 5）只能向下移动
            if (fromY < 5 && toY <= fromY)
            {
                return false;
            }
            // 黑卒过河后（y >= 5）可以左右移动
            if (fromY >= 5 && dx == 1 && dy == 0)
            {
                return true;
            }
            // 黑卒任何时候都不能向上移动
            if (toY < fromY)
            {
                return false;
            }
        }

        return true;
    }
};

// 初始化静态成员
Player Board::currentPlayer = RED;

// 游戏类
class Game
{
private:
    Board board;
    int cursorX, cursorY; // 光标位置

public:
    Game() : cursorX(0), cursorY(0) {}

    void run()
    {
        while (true)
        {
            // 绘制棋盘
            board.draw();

            // 处理输入
            bool moved = board.handleInput(cursorX, cursorY, Board::currentPlayer);

            // 检查游戏是否结束
            if (board.isGeneralCaptured(RED))
            {
                board.draw();
                cout << "黑方胜利！" << endl;
                break;
            }
            if (board.isGeneralCaptured(BLACK))
            {
                board.draw();
                cout << "\033[31m红方胜利！\033[0m" << endl;
                break;
            }

            // 切换玩家
            if (moved)
            {
                Board::currentPlayer = (Board::currentPlayer == RED) ? BLACK : RED;
            }
        }

        cout << "按任意键退出..." << endl;
        _getch();
    }
};

int main()

{
    // 设置控制台编码为UTF-8
    SetConsoleOutputCP(65001);
    SetConsoleCP(65001);

    // 原有的代码...
    system("chcp 65001"); // 保留这句，双重保障

    cout << "欢迎来到中国象棋游戏！" << endl;
    cout << "按任意键开始游戏..." << endl;
    _getch();

    Game game;
    game.run();

    return 0;
}
