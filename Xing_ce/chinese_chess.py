import pygame
import sys

# 初始化pygame
pygame.init()

# 确保中文显示正常
pygame.font.init()

# 游戏常量
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 1000
BOARD_SIZE = 9  # 9列
BOARD_ROWS = 10  # 10行
CELL_SIZE = 80
BOARD_LEFT = (WINDOW_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
BOARD_TOP = (WINDOW_HEIGHT - BOARD_ROWS * CELL_SIZE) // 2

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("中国象棋")

# 尝试加载中文字体
try:
    font = pygame.font.Font("simhei.ttf", 40)  # 尝试加载系统中的黑体
except:
    # 如果指定字体加载失败，使用默认字体
    font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 40)

# 棋子类型枚举
class PieceType:
    NONE = 0
    R_GENERAL = 1    # 红帅
    R_ADVISOR = 2    # 红仕
    R_ELEPHANT = 3   # 红相
    R_HORSE = 4      # 红马
    R_CHARIOT = 5    # 红车
    R_CANNON = 6     # 红炮
    R_SOLDIER = 7    # 红兵
    B_GENERAL = 8    # 黑将
    B_ADVISOR = 9    # 黑士
    B_ELEPHANT = 10  # 黑象
    B_HORSE = 11     # 黑马
    B_CHARIOT = 12   # 黑车
    B_CANNON = 13    # 黑炮
    B_SOLDIER = 14   # 黑卒

# 玩家枚举
class Player:
    RED = 1
    BLACK = 2

# 棋子类
class Piece:
    def __init__(self, piece_type, x, y):
        self.type = piece_type
        self.x = x  # 列
        self.y = y  # 行
        self.alive = True
        
    def get_player(self):
        if self.type >= PieceType.R_GENERAL and self.type <= PieceType.R_SOLDIER:
            return Player.RED
        return Player.BLACK
        
    def get_name(self):
        names = {
            PieceType.R_GENERAL: "帅",
            PieceType.R_ADVISOR: "仕",
            PieceType.R_ELEPHANT: "相",
            PieceType.R_HORSE: "马",
            PieceType.R_CHARIOT: "车",
            PieceType.R_CANNON: "炮",
            PieceType.R_SOLDIER: "兵",
            PieceType.B_GENERAL: "将",
            PieceType.B_ADVISOR: "士",
            PieceType.B_ELEPHANT: "象",
            PieceType.B_HORSE: "马",
            PieceType.B_CHARIOT: "车",
            PieceType.B_CANNON: "炮",
            PieceType.B_SOLDIER: "卒"
        }
        return names.get(self.type, "")

# 棋盘类
class Board:
    def __init__(self):
        self.pieces = []
        self.selected_piece = None
        self.current_player = Player.RED
        self.init_pieces()
        
    def init_pieces(self):
        # 红方棋子
        self.pieces.append(Piece(PieceType.R_GENERAL, 4, 9))
        self.pieces.append(Piece(PieceType.R_ADVISOR, 3, 9))
        self.pieces.append(Piece(PieceType.R_ADVISOR, 5, 9))
        self.pieces.append(Piece(PieceType.R_ELEPHANT, 2, 9))
        self.pieces.append(Piece(PieceType.R_ELEPHANT, 6, 9))
        self.pieces.append(Piece(PieceType.R_HORSE, 1, 9))
        self.pieces.append(Piece(PieceType.R_HORSE, 7, 9))
        self.pieces.append(Piece(PieceType.R_CHARIOT, 0, 9))
        self.pieces.append(Piece(PieceType.R_CHARIOT, 8, 9))
        self.pieces.append(Piece(PieceType.R_CANNON, 1, 7))
        self.pieces.append(Piece(PieceType.R_CANNON, 7, 7))
        self.pieces.append(Piece(PieceType.R_SOLDIER, 0, 6))
        self.pieces.append(Piece(PieceType.R_SOLDIER, 2, 6))
        self.pieces.append(Piece(PieceType.R_SOLDIER, 4, 6))
        self.pieces.append(Piece(PieceType.R_SOLDIER, 6, 6))
        self.pieces.append(Piece(PieceType.R_SOLDIER, 8, 6))
        
        # 黑方棋子
        self.pieces.append(Piece(PieceType.B_GENERAL, 4, 0))
        self.pieces.append(Piece(PieceType.B_ADVISOR, 3, 0))
        self.pieces.append(Piece(PieceType.B_ADVISOR, 5, 0))
        self.pieces.append(Piece(PieceType.B_ELEPHANT, 2, 0))
        self.pieces.append(Piece(PieceType.B_ELEPHANT, 6, 0))
        self.pieces.append(Piece(PieceType.B_HORSE, 1, 0))
        self.pieces.append(Piece(PieceType.B_HORSE, 7, 0))
        self.pieces.append(Piece(PieceType.B_CHARIOT, 0, 0))
        self.pieces.append(Piece(PieceType.B_CHARIOT, 8, 0))
        self.pieces.append(Piece(PieceType.B_CANNON, 1, 2))
        self.pieces.append(Piece(PieceType.B_CANNON, 7, 2))
        self.pieces.append(Piece(PieceType.B_SOLDIER, 0, 3))
        self.pieces.append(Piece(PieceType.B_SOLDIER, 2, 3))
        self.pieces.append(Piece(PieceType.B_SOLDIER, 4, 3))
        self.pieces.append(Piece(PieceType.B_SOLDIER, 6, 3))
        self.pieces.append(Piece(PieceType.B_SOLDIER, 8, 3))
    
    def get_piece_at(self, x, y):
        for piece in self.pieces:
            if piece.alive and piece.x == x and piece.y == y:
                return piece
        return None
    
    def is_valid_move(self, from_x, from_y, to_x, to_y):
        # 检查是否在棋盘范围内
        if to_x < 0 or to_x >= BOARD_SIZE or to_y < 0 or to_y >= BOARD_ROWS:
            return False
        
        piece = self.get_piece_at(from_x, from_y)
        if not piece:
            return False
            
        # 不能吃自己的棋子
        target = self.get_piece_at(to_x, to_y)
        if target and target.get_player() == piece.get_player():
            return False
        
        # 根据不同棋子类型检查移动规则
        if piece.type in (PieceType.R_GENERAL, PieceType.B_GENERAL):
            return self.is_valid_general_move(piece, from_x, from_y, to_x, to_y)
        elif piece.type in (PieceType.R_ADVISOR, PieceType.B_ADVISOR):
            return self.is_valid_advisor_move(piece, from_x, from_y, to_x, to_y)
        elif piece.type in (PieceType.R_ELEPHANT, PieceType.B_ELEPHANT):
            return self.is_valid_elephant_move(piece, from_x, from_y, to_x, to_y)
        elif piece.type in (PieceType.R_HORSE, PieceType.B_HORSE):
            return self.is_valid_horse_move(piece, from_x, from_y, to_x, to_y)
        elif piece.type in (PieceType.R_CHARIOT, PieceType.B_CHARIOT):
            return self.is_valid_chariot_move(piece, from_x, from_y, to_x, to_y)
        elif piece.type in (PieceType.R_CANNON, PieceType.B_CANNON):
            return self.is_valid_cannon_move(piece, from_x, from_y, to_x, to_y)
        elif piece.type in (PieceType.R_SOLDIER, PieceType.B_SOLDIER):
            return self.is_valid_soldier_move(piece, from_x, from_y, to_x, to_y)
        
        return False
    
    def is_valid_general_move(self, piece, from_x, from_y, to_x, to_y):
        # 将帅照面检查
        target = self.get_piece_at(to_x, to_y)
        if (piece.type == PieceType.R_GENERAL and target and target.type == PieceType.B_GENERAL) or \
           (piece.type == PieceType.B_GENERAL and target and target.type == PieceType.R_GENERAL):
            if from_x == to_x:  # 同一列
                # 检查中间是否有棋子
                min_y, max_y = min(from_y, to_y), max(from_y, to_y)
                has_obstacle = False
                for y in range(min_y + 1, max_y):
                    if self.get_piece_at(from_x, y):
                        has_obstacle = True
                        break
                if not has_obstacle:
                    return True
        
        # 九宫格限制
        if piece.type == PieceType.R_GENERAL:  # 红帅
            if not (3 <= to_x <= 5 and 7 <= to_y <= 9):
                return False
        else:  # 黑将
            if not (3 <= to_x <= 5 and 0 <= to_y <= 2):
                return False
        
        # 只能走一步
        dx = abs(from_x - to_x)
        dy = abs(from_y - to_y)
        return (dx == 0 and dy == 1) or (dx == 1 and dy == 0)
    
    def is_valid_advisor_move(self, piece, from_x, from_y, to_x, to_y):
        # 九宫格限制
        if piece.type == PieceType.R_ADVISOR:  # 红仕
            if not (3 <= to_x <= 5 and 7 <= to_y <= 9):
                return False
        else:  # 黑士
            if not (3 <= to_x <= 5 and 0 <= to_y <= 2):
                return False
        
        # 只能斜走一步
        dx = abs(from_x - to_x)
        dy = abs(from_y - to_y)
        return dx == 1 and dy == 1
    
    def is_valid_elephant_move(self, piece, from_x, from_y, to_x, to_y):
        # 不能过河
        if piece.type == PieceType.R_ELEPHANT and to_y < 5:  # 红相
            return False
        if piece.type == PieceType.B_ELEPHANT and to_y > 4:  # 黑象
            return False
        
        # 走田字格
        dx = abs(from_x - to_x)
        dy = abs(from_y - to_y)
        if dx != 2 or dy != 2:
            return False
        
        # 检查象眼
        eye_x = from_x + (to_x - from_x) // 2
        eye_y = from_y + (to_y - from_y) // 2
        return self.get_piece_at(eye_x, eye_y) is None
    
    def is_valid_horse_move(self, piece, from_x, from_y, to_x, to_y):
        dx = abs(from_x - to_x)
        dy = abs(from_y - to_y)
        
        # 马走日
        if not ((dx == 1 and dy == 2) or (dx == 2 and dy == 1)):
            return False
        
        # 检查马腿
        if dx == 2:
            leg_x = from_x + (to_x - from_x) // 2
            leg_y = from_y
        else:
            leg_x = from_x
            leg_y = from_y + (to_y - from_y) // 2
            
        return self.get_piece_at(leg_x, leg_y) is None
    
    def is_valid_chariot_move(self, piece, from_x, from_y, to_x, to_y):
        # 必须直线移动
        if from_x != to_x and from_y != to_y:
            return False
        
        # 检查路径上是否有障碍物
        if from_x == to_x:  # 上下移动
            min_y, max_y = min(from_y, to_y), max(from_y, to_y)
            for y in range(min_y + 1, max_y):
                if self.get_piece_at(from_x, y):
                    return False
        else:  # 左右移动
            min_x, max_x = min(from_x, to_x), max(from_x, to_x)
            for x in range(min_x + 1, max_x):
                if self.get_piece_at(x, from_y):
                    return False
                    
        return True
    
    def is_valid_cannon_move(self, piece, from_x, from_y, to_x, to_y):
        # 必须直线移动
        if from_x != to_x and from_y != to_y:
            return False
        
        # 计算路径上的棋子数量
        obstacle_count = 0
        if from_x == to_x:  # 上下移动
            min_y, max_y = min(from_y, to_y), max(from_y, to_y)
            for y in range(min_y + 1, max_y):
                if self.get_piece_at(from_x, y):
                    obstacle_count += 1
        else:  # 左右移动
            min_x, max_x = min(from_x, to_x), max(from_x, to_x)
            for x in range(min_x + 1, max_x):
                if self.get_piece_at(x, from_y):
                    obstacle_count += 1
        
        # 炮翻山吃子
        target = self.get_piece_at(to_x, to_y)
        if target:  # 吃子需要一个炮架
            return obstacle_count == 1
        else:  # 移动不能有炮架
            return obstacle_count == 0
    
    def is_valid_soldier_move(self, piece, from_x, from_y, to_x, to_y):
        dx = abs(from_x - to_x)
        dy = abs(from_y - to_y)
        
        # 只能走一步
        if dx + dy != 1:
            return False
        
        # 红兵（不能后退）
        if piece.type == PieceType.R_SOLDIER:
            if to_y > from_y:  # 红兵不能向下走（后退）
                return False
            # 过河后才能左右走
            if dx == 1 and from_y > 4:  # 未过河不能左右走
                return False
        
        # 黑卒（不能后退）
        if piece.type == PieceType.B_SOLDIER:
            if to_y < from_y:  # 黑卒不能向上走（后退）
                return False
            # 过河后才能左右走
            if dx == 1 and from_y < 5:  # 未过河不能左右走
                return False
                
        return True
    
    def move_piece(self, from_x, from_y, to_x, to_y):
        if not self.is_valid_move(from_x, from_y, to_x, to_y):
            return False
        
        piece = self.get_piece_at(from_x, from_y)
        target = self.get_piece_at(to_x, to_y)
        
        # 吃掉对方棋子
        if target:
            target.alive = False
        
        # 移动棋子
        piece.x = to_x
        piece.y = to_y
        
        # 切换玩家
        self.current_player = Player.BLACK if self.current_player == Player.RED else Player.RED
        self.selected_piece = None
        return True
    
    def is_game_over(self):
        # 检查将/帅是否被吃掉
        has_r_general = any(p.type == PieceType.R_GENERAL and p.alive for p in self.pieces)
        has_b_general = any(p.type == PieceType.B_GENERAL and p.alive for p in self.pieces)
        
        if not has_r_general:
            return "黑方胜利！"
        if not has_b_general:
            return "红方胜利！"
        return None
    
    def draw(self, screen):
        # 绘制棋盘背景
        screen.fill(BROWN)
        
        # 绘制棋盘线条
        for i in range(BOARD_ROWS):
            y = BOARD_TOP + i * CELL_SIZE
            # 楚河汉界
            if i == 0 or i == 9:
                pygame.draw.line(screen, BLACK, 
                                (BOARD_LEFT, y), 
                                (BOARD_LEFT + (BOARD_SIZE - 1) * CELL_SIZE, y), 
                                2)
            else:
                # 中间楚河汉界断开
                if i == 4 or i == 5:
                    pygame.draw.line(screen, BLACK, 
                                    (BOARD_LEFT, y), 
                                    (BOARD_LEFT + 4 * CELL_SIZE, y), 
                                    2)
                    pygame.draw.line(screen, BLACK, 
                                    (BOARD_LEFT + 5 * CELL_SIZE, y), 
                                    (BOARD_LEFT + 8 * CELL_SIZE, y), 
                                    2)
                else:
                    pygame.draw.line(screen, BLACK, 
                                    (BOARD_LEFT, y), 
                                    (BOARD_LEFT + (BOARD_SIZE - 1) * CELL_SIZE, y), 
                                    2)
        
        # 绘制列线
        for i in range(BOARD_SIZE):
            x = BOARD_LEFT + i * CELL_SIZE
            # 河界上下的线
            pygame.draw.line(screen, BLACK, 
                            (x, BOARD_TOP), 
                            (x, BOARD_TOP + 4 * CELL_SIZE), 
                            2)
            pygame.draw.line(screen, BLACK, 
                            (x, BOARD_TOP + 5 * CELL_SIZE), 
                            (x, BOARD_TOP + 9 * CELL_SIZE), 
                            2)
        
        # 绘制九宫格斜线
        # 上方九宫
        pygame.draw.line(screen, BLACK, 
                        (BOARD_LEFT + 3 * CELL_SIZE, BOARD_TOP), 
                        (BOARD_LEFT + 5 * CELL_SIZE, BOARD_TOP + 2 * CELL_SIZE), 
                        2)
        pygame.draw.line(screen, BLACK, 
                        (BOARD_LEFT + 5 * CELL_SIZE, BOARD_TOP), 
                        (BOARD_LEFT + 3 * CELL_SIZE, BOARD_TOP + 2 * CELL_SIZE), 
                        2)
        
        # 下方九宫
        pygame.draw.line(screen, BLACK, 
                        (BOARD_LEFT + 3 * CELL_SIZE, BOARD_TOP + 7 * CELL_SIZE), 
                        (BOARD_LEFT + 5 * CELL_SIZE, BOARD_TOP + 9 * CELL_SIZE), 
                        2)
        pygame.draw.line(screen, BLACK, 
                        (BOARD_LEFT + 5 * CELL_SIZE, BOARD_TOP + 7 * CELL_SIZE), 
                        (BOARD_LEFT + 3 * CELL_SIZE, BOARD_TOP + 9 * CELL_SIZE), 
                        2)
        
        # 绘制楚河汉界文字
        river_text = font.render("楚 河", True, BLACK)
        screen.blit(river_text, (BOARD_LEFT + CELL_SIZE * 1, BOARD_TOP + CELL_SIZE * 4 + 10))
        river_text = font.render("汉 界", True, BLACK)
        screen.blit(river_text, (BOARD_LEFT + CELL_SIZE * 6, BOARD_TOP + CELL_SIZE * 4 + 10))
        
        # 绘制棋子
        for piece in self.pieces:
            if piece.alive:
                x = BOARD_LEFT + piece.x * CELL_SIZE
                y = BOARD_TOP + piece.y * CELL_SIZE
                
                # 绘制棋子背景
                color = RED if piece.get_player() == Player.RED else BLACK
                pygame.draw.circle(screen, WHITE, (x, y), CELL_SIZE // 2 - 5)
                pygame.draw.circle(screen, color, (x, y), CELL_SIZE // 2 - 5, 2)
                
                # 绘制棋子文字
                text = font.render(piece.get_name(), True, color)
                text_rect = text.get_rect(center=(x, y))
                screen.blit(text, text_rect)
        
        # 绘制选中效果
        if self.selected_piece:
            x = BOARD_LEFT + self.selected_piece.x * CELL_SIZE
            y = BOARD_TOP + self.selected_piece.y * CELL_SIZE
            pygame.draw.circle(screen, YELLOW, (x, y), CELL_SIZE // 2, 3)
        
        # 显示当前玩家
        player_text = "当前回合: 红方" if self.current_player == Player.RED else "当前回合: 黑方"
        text = font.render(player_text, True, RED if self.current_player == Player.RED else BLACK)
        screen.blit(text, (50, 50))
        
        # 显示操作说明
        instructions = font.render("操作: 点击选择棋子，再次点击目标位置移动", True, BLACK)
        screen.blit(instructions, (50, WINDOW_HEIGHT - 80))
        
        # 检查游戏是否结束
        game_result = self.is_game_over()
        if game_result:
            # 创建半透明遮罩
            s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 128))
            screen.blit(s, (0, 0))
            
            # 显示结果文字
            result_text = font.render(game_result, True, YELLOW)
            text_rect = result_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(result_text, text_rect)
            
            # 显示重新开始提示
            restart_text = font.render("按R键重新开始", True, YELLOW)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            screen.blit(restart_text, restart_rect)

# 游戏主类
class Game:
    def __init__(self):
        self.board = Board()
        self.running = True
        self.clock = pygame.time.Clock()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # 重新开始游戏
                    self.board = Board()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
                x, y = pygame.mouse.get_pos()
                
                # 计算点击的棋盘位置
                board_x = (x - BOARD_LEFT) // CELL_SIZE
                board_y = (y - BOARD_TOP) // CELL_SIZE
                
                # 检查是否在棋盘范围内
                if 0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_ROWS:
                    piece = self.board.get_piece_at(board_x, board_y)
                    
                    # 如果点击了当前玩家的棋子，则选中它
                    if piece and piece.get_player() == self.board.current_player:
                        self.board.selected_piece = piece
                    # 如果已经选中棋子，尝试移动
                    elif self.board.selected_piece:
                        self.board.move_piece(
                            self.board.selected_piece.x, 
                            self.board.selected_piece.y, 
                            board_x, 
                            board_y
                        )
    
    def run(self):
        while self.running:
            self.handle_events()
            self.board.draw(screen)
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

# 启动游戏
if __name__ == "__main__":
    game = Game()
    game.run()
    