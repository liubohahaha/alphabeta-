from GameMap import *
from enum import IntEnum
from random import randint
import time

AI_SEARCH_DEPTH = 4
AI_LIMITED_MOVE_NUM = 20


class CHESS_TYPE(IntEnum):
    NONE = 0,
    SLEEP_TWO = 1,
    LIVE_TWO = 2,
    SLEEP_THREE = 3
    LIVE_THREE = 4,
    CHONG_FOUR = 5,
    LIVE_FOUR = 6,
    LIVE_FIVE = 7,


CHESS_TYPE_NUM = 8

FIVE = CHESS_TYPE.LIVE_FIVE.value
FOUR, THREE, TWO = CHESS_TYPE.LIVE_FOUR.value, CHESS_TYPE.LIVE_THREE.value, CHESS_TYPE.LIVE_TWO.value
SFOUR, STHREE, STWO = CHESS_TYPE.CHONG_FOUR.value, CHESS_TYPE.SLEEP_THREE.value, CHESS_TYPE.SLEEP_TWO.value

SCORE_MAX = 0x7fffffff
SCORE_MIN = -1 * SCORE_MAX
SCORE_FIVE, SCORE_FOUR, SCORE_SFOUR = 100000, 10000, 1000
SCORE_THREE, SCORE_STHREE, SCORE_TWO, SCORE_STWO = 100, 10, 8, 2


class Computer():
    def __init__(self, chess_len):
        self.len = chess_len
        # [horizon, vertical, left diagonal, right diagonal]
        self.isAnalysis = [[[0, 0, 0, 0] for x in range(chess_len)] for y in range(chess_len)]
        self.count_QiXing = [[0 for x in range(CHESS_TYPE_NUM)] for i in range(2)]

    def click(self, map, x, y, turn):
        map.click(x, y, turn)

    def isWin(self, board, turn):
        return self.caculate_score_of_Current_Situation(board, turn, True)

    # evaluate score of point, to improve pruning efficiency
    # 假设棋子落下，评估最高得分的落子点的位置
    def caculate_Score_After_Chessing(self, board, x, y, me, opp):
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        for i in range(len(self.count_QiXing)):
            for j in range(len(self.count_QiXing[0])):
                self.count_QiXing[i][j] = 0
        # 假设落自己的棋
        board[y][x] = me
        self.integrate_QIXING_of_Current_Situation(board, x, y, me, opp, self.count_QiXing[me - 1])
        me_QiXingcount = self.count_QiXing[me - 1]
        # 假设落对方的棋
        board[y][x] = opp
        self.integrate_QIXING_of_Current_Situation(board, x, y, opp, me, self.count_QiXing[opp - 1])
        opp_QiXing_count = self.count_QiXing[opp - 1]
        # 回退
        board[y][x] = 0

        mscore = self.estimate_Current_Score(me_QiXingcount)
        oscore = self.estimate_Current_Score(opp_QiXing_count)

        return (mscore, oscore)

    # check if has a none empty position in it's radius range
    # 判断该可能落子点的周围点是否有棋子
    def isSurrounded(self, board, x, y, radius):
        start_x, end_x = (x - radius), (x + radius)
        start_y, end_y = (y - radius), (y + radius)

        for i in range(start_y, end_y + 1):
            for j in range(start_x, end_x + 1):
                if i >= 0 and i < self.len and j >= 0 and j < self.len:
                    if board[i][j] != 0:
                        return True
        return False

    # get all positions near chess
    # 确定价值较高的可落子点
    def generate_All_Can_Move_Entry(self, board, turn):
        fives = []
        mfours, ofours = [], []
        msfours, osfours = [], []
        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            me = 1
            opp = 2
        else:
            me = 2
            opp = 1

        moves = []
        radius = 1

        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == 0 and self.isSurrounded(board, x, y, radius):
                    mscore, oscore = self.caculate_Score_After_Chessing(board, x, y, me, opp)
                    point = (max(mscore, oscore), x, y)

                    if mscore >= SCORE_FIVE or oscore >= SCORE_FIVE:
                        fives.append(point)
                    elif mscore >= SCORE_FOUR:
                        mfours.append(point)
                    elif oscore >= SCORE_FOUR:
                        ofours.append(point)
                    elif mscore >= SCORE_SFOUR:
                        msfours.append(point)
                    elif oscore >= SCORE_SFOUR:
                        osfours.append(point)

                    moves.append(point)

        if len(fives) > 0: return fives

        if len(mfours) > 0: return mfours

        if len(ofours) > 0:
            if len(msfours) == 0:
                return ofours
            else:
                return ofours + msfours

        moves.sort(reverse=True)

        # FIXME: decrease think time: only consider limited moves with higher scores
        if self.maxdepth > 2 and len(moves) > AI_LIMITED_MOVE_NUM:
            moves = moves[:AI_LIMITED_MOVE_NUM]
        return moves
    # 迭代进行alphabeta剪枝
    def alpha_Beta_search(self, board, turn, depth, alpha=SCORE_MIN, beta=SCORE_MAX):
        score = self.caculate_score_of_Current_Situation(board, turn)
        if depth <= 0 or abs(score) >= SCORE_FIVE:
            return score

        moves = self.generate_All_Can_Move_Entry(board, turn)
        bestmove = None
        self.alpha += len(moves)

        # if there are no moves, just return the score
        if len(moves) == 0:
            return score

        for _, x, y in moves:
            board[y][x] = turn

            if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
                op_turn = MAP_ENTRY_TYPE.MAP_PLAYER_TWO
            else:
                op_turn = MAP_ENTRY_TYPE.MAP_PLAYER_ONE

            score = - self.alpha_Beta_search(board, op_turn, depth - 1, -beta, -alpha)

            board[y][x] = 0
            self.belta += 1

            # alphabeta 剪枝
            if score > alpha:
                alpha = score
                bestmove = (x, y)
                if alpha >= beta:
                    break

        if depth == self.maxdepth and bestmove:
            self.bestmove = bestmove

        return alpha

    # 设定迭代搜索深度
    def start_search(self, board, turn, depth=4):
        self.maxdepth = depth
        self.bestmove = None
        score = self.alpha_Beta_search(board, turn, depth)
        x, y = self.bestmove
        return score, x, y

    def find_Best_Position(self, board, turn):
        time1 = time.time()
        self.alpha = 0
        self.belta = 0
        score, x, y = self.start_search(board, turn, AI_SEARCH_DEPTH)
        time2 = time.time()
        print('time[%.2f] (%d, %d), score[%d] alpha[%d] belta[%d]' % (
            (time2 - time1), x, y, score, self.alpha, self.belta))
        return (x, y)

    # 估计落棋后的局面的分数
    def estimate_Current_Score(self, count_QiXing):
        score = 0
        if count_QiXing[FIVE] > 0:
            return SCORE_FIVE

        if count_QiXing[FOUR] > 0:
            return SCORE_FOUR

        if count_QiXing[SFOUR] > 1:
            score += count_QiXing[SFOUR] * SCORE_SFOUR
        elif count_QiXing[SFOUR] > 0 and count_QiXing[THREE] > 0:
            score += count_QiXing[SFOUR] * SCORE_SFOUR
        elif count_QiXing[SFOUR] > 0:
            score += SCORE_THREE

        if count_QiXing[THREE] > 1:
            score += 5 * SCORE_THREE
        elif count_QiXing[THREE] > 0:
            score += SCORE_THREE

        if count_QiXing[STHREE] > 0:
            score += count_QiXing[STHREE] * SCORE_STHREE
        if count_QiXing[TWO] > 0:
            score += count_QiXing[TWO] * SCORE_TWO
        if count_QiXing[STWO] > 0:
            score += count_QiXing[STWO] * SCORE_STWO

        return score

    # 根据自己的棋型状态和对手的棋型状态计算分数
    def caculate_Current_Score(self, me_QiXingcount, opp_QiXing_count):
        mscore, oscore = 0, 0
        if me_QiXingcount[FIVE] > 0:
            return (SCORE_FIVE, 0)
        if opp_QiXing_count[FIVE] > 0:
            return (0, SCORE_FIVE)

        if me_QiXingcount[SFOUR] >= 2:
            me_QiXingcount[FOUR] += 1
        if opp_QiXing_count[SFOUR] >= 2:
            opp_QiXing_count[FOUR] += 1

        if me_QiXingcount[FOUR] > 0:
            return (9050, 0)
        if me_QiXingcount[SFOUR] > 0:
            return (9040, 0)

        if opp_QiXing_count[FOUR] > 0:
            return (0, 9030)
        if opp_QiXing_count[SFOUR] > 0 and opp_QiXing_count[THREE] > 0:
            return (0, 9020)

        if me_QiXingcount[THREE] > 0 and opp_QiXing_count[SFOUR] == 0:
            return (9010, 0)

        if (opp_QiXing_count[THREE] > 1 and me_QiXingcount[THREE] == 0 and me_QiXingcount[STHREE] == 0):
            return (0, 9000)

        if opp_QiXing_count[SFOUR] > 0:
            oscore += 400

        if me_QiXingcount[THREE] > 1:
            mscore += 500
        elif me_QiXingcount[THREE] > 0:
            mscore += 100

        if opp_QiXing_count[THREE] > 1:
            oscore += 2000
        elif opp_QiXing_count[THREE] > 0:
            oscore += 400

        if me_QiXingcount[STHREE] > 0:
            mscore += me_QiXingcount[STHREE] * 10
        if opp_QiXing_count[STHREE] > 0:
            oscore += opp_QiXing_count[STHREE] * 10

        if me_QiXingcount[TWO] > 0:
            mscore += me_QiXingcount[TWO] * 6
        if opp_QiXing_count[TWO] > 0:
            oscore += opp_QiXing_count[TWO] * 6

        if me_QiXingcount[STWO] > 0:
            mscore += me_QiXingcount[STWO] * 2
        if opp_QiXing_count[STWO] > 0:
            oscore += opp_QiXing_count[STWO] * 2

        return (mscore, oscore)

    # 计算当前局面的自己的分数和对手的分数
    def caculate_score_of_Current_Situation(self, board, turn, checkWin=False):
        # 重置
        for y in range(self.len):
            for x in range(self.len):
                for i in range(4):
                    self.isAnalysis[y][x][i] = 0
        # 判断最近一手棋该哪方下子
        for i in range(len(self.count_QiXing)):
            for j in range(len(self.count_QiXing[0])):
                self.count_QiXing[i][j] = 0

        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            me = 1
            opp = 2
        else:
            me = 2
            opp = 1

        for y in range(self.len):
            for x in range(self.len):
                if board[y][x] == me:
                    self.integrate_QIXING_of_Current_Situation(board, x, y, me, opp)
                elif board[y][x] == opp:
                    self.integrate_QIXING_of_Current_Situation(board, x, y, opp, me)
        # 自己棋型的状态
        me_QiXingcount = self.count_QiXing[me - 1]
        # 对手棋型的状态
        opp_QiXing_count = self.count_QiXing[opp - 1]
        if checkWin:
            return me_QiXingcount[FIVE] > 0
        else:
            # 获取当前局面的自己分数和对手的分数
            mscore, oscore = self.caculate_Current_Score(me_QiXingcount, opp_QiXing_count)
            return (mscore - oscore)

    # 对于一个位置的四个方向分别进行检查，mine表示自己棋的值，opponent表示对手棋的值。 mine此处传值为2，opponent为1
    # 整合当前局面的棋型状态
    def integrate_QIXING_of_Current_Situation(self, board, x, y, me, opp, count_QiXing=None):
        dir_offset = [(1, 0), (0, 1), (1, 1), (1, -1)]  # direction from left to right
        ignore_record = True
        if count_QiXing is None:
            count_QiXing = self.count_QiXing[me - 1]
            ignore_record = False
        # 统计四个方向上的棋型
        for i in range(4):
            if self.isAnalysis[y][x][i] == 0 or ignore_record:
                self.integrate_QIXING_of_One_Direction(board, x, y, i, dir_offset[i], me, opp, count_QiXing)

    # 获取一个方向上的一行
    def get_Line_of_One_Direction(self, board, x, y, dir_offset, mine, opp):
        line = [0 for i in range(9)]

        tmp_x = x + (-5 * dir_offset[0])
        tmp_y = y + (-5 * dir_offset[1])
        for i in range(9):
            tmp_x += dir_offset[0]
            tmp_y += dir_offset[1]
            # 超出了棋盘范围，设为对手
            if (tmp_x < 0 or tmp_x >= self.len or
                    tmp_y < 0 or tmp_y >= self.len):
                line[i] = opp  # set out of range as opp chess
            else:
                line[i] = board[tmp_y][tmp_x]
        return line

    # 整合一个方向上的棋型数量
    def integrate_QIXING_of_One_Direction(self, board, x, y, dir_index, dir, me, opp, count_QiXing):
    # 记录该方向上已被分析过棋位置
        def setRecord(self, x, y, left, right, dir_index, dir_offset):
            tmp_x = x + (-5 + left) * dir_offset[0]
            tmp_y = y + (-5 + left) * dir_offset[1]
            for i in range(left, right + 1):
                tmp_x += dir_offset[0]
                tmp_y += dir_offset[1]
                self.isAnalysis[tmp_y][tmp_x][dir_index] = 1

        # 获取一条线上的9子
        line = self.get_Line_of_One_Direction(board, x, y, dir, me, opp)

        empty = MAP_ENTRY_TYPE.MAP_EMPTY.value
        left_idx, right_idx = 4, 4
        while right_idx < 8:
            if line[right_idx + 1] != me:
                break
            right_idx += 1
        while left_idx > 0:
            if line[left_idx - 1] != me:
                break
            left_idx -= 1

        left_range, right_range = left_idx, right_idx
        while right_range < 8:
            if line[right_range + 1] == opp:
                break
            right_range += 1
        while left_range > 0:
            if line[left_range - 1] == opp:
                break
            left_range -= 1
        # 含有空点的与中心点相连的数量
        chess_range = right_range - left_range + 1
        if chess_range < 5:
            setRecord(self, x, y, left_range, right_range, dir_index, dir)
            return CHESS_TYPE.NONE

        setRecord(self, x, y, left_idx, right_idx, dir_index, dir)
        # 与中心点相连的同色棋的数量
        m_range = right_idx - left_idx + 1

        if m_range >= 5:
            count_QiXing[FIVE] += 1

        # 活四: XMMMMX
        # 冲四: XMMMMP, PMMMMX
        if m_range == 4:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                left_empty = True
            if line[right_idx + 1] == empty:
                right_empty = True
            if left_empty and right_empty:
                count_QiXing[FOUR] += 1
            elif left_empty or right_empty:
                count_QiXing[SFOUR] += 1

        # 冲四 : MXMMM, MMMXM, the two types can both exist
        # 活三 : XMMMXX, XXMMMX
        # 眠三 : PMMMX, XMMMP, PXMMMXP
        if m_range == 3:
            left_empty = right_empty = False
            left_four = right_four = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == me:  # MXMMM
                    setRecord(self, x, y, left_idx - 2, left_idx - 1, dir_index, dir)
                    count_QiXing[SFOUR] += 1
                    left_four = True
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == me:  # MMMXM
                    setRecord(self, x, y, right_idx + 1, right_idx + 2, dir_index, dir)
                    count_QiXing[SFOUR] += 1
                    right_four = True
                right_empty = True

            if left_four or right_four:
                pass
            elif left_empty and right_empty:
                if chess_range > 5:  # XMMMXX, XXMMMX
                    count_QiXing[THREE] += 1
                else:  # PXMMMXP
                    count_QiXing[STHREE] += 1
            elif left_empty or right_empty:  # PMMMX, XMMMP
                count_QiXing[STHREE] += 1

        # 冲四: MMXMM, only check right direction
        # 活三: XMXMMX, XMMXMX the two types can both exist
        # 眠三: PMXMMX, XMXMMP, PMMXMX, XMMXMP
        # 活二: XMMX
        # 眠二: PMMX, XMMP
        if m_range == 2:
            left_empty = right_empty = False
            left_three = right_three = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == me:
                    setRecord(self, x, y, left_idx - 2, left_idx - 1, dir_index, dir)
                    if line[left_idx - 3] == empty:
                        if line[right_idx + 1] == empty:  # XMXMMX
                            count_QiXing[THREE] += 1
                        else:  # XMXMMP
                            count_QiXing[STHREE] += 1
                        left_three = True
                    elif line[left_idx - 3] == opp:  # PMXMMX
                        if line[right_idx + 1] == empty:
                            count_QiXing[STHREE] += 1
                            left_three = True

                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == me:
                    if line[right_idx + 3] == me:  # MMXMM
                        setRecord(self, x, y, right_idx + 1, right_idx + 2, dir_index, dir)
                        count_QiXing[SFOUR] += 1
                        right_three = True
                    elif line[right_idx + 3] == empty:
                        # setRecord(self, x, y, right_idx+1, right_idx+2, dir_index, dir)
                        if left_empty:  # XMMXMX
                            count_QiXing[THREE] += 1
                        else:  # PMMXMX
                            count_QiXing[STHREE] += 1
                        right_three = True
                    elif left_empty:  # XMMXMP
                        count_QiXing[STHREE] += 1
                        right_three = True

                right_empty = True

            if left_three or right_three:
                pass
            elif left_empty and right_empty:  # XMMX
                count_QiXing[TWO] += 1
            elif left_empty or right_empty:  # PMMX, XMMP
                count_QiXing[STWO] += 1

        # 活二: XMXMX, XMXXMX only check right direction
        # 眠二: PMXMX, XMXMP
        if m_range == 1:
            left_empty = right_empty = False
            if line[left_idx - 1] == empty:
                if line[left_idx - 2] == me:
                    if line[left_idx - 3] == empty:
                        if line[right_idx + 1] == opp:  # XMXMP
                            count_QiXing[STWO] += 1
                left_empty = True

            if line[right_idx + 1] == empty:
                if line[right_idx + 2] == me:
                    if line[right_idx + 3] == empty:
                        if left_empty:  # XMXMX
                            # setRecord(self, x, y, left_idx, right_idx+2, dir_index, dir)
                            count_QiXing[TWO] += 1
                        else:  # PMXMX
                            count_QiXing[STWO] += 1
                elif line[right_idx + 2] == empty:
                    if line[right_idx + 3] == me and line[right_idx + 4] == empty:  # XMXXMX
                        count_QiXing[TWO] += 1

        return CHESS_TYPE.NONE
