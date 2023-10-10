import cv2 as cv
import numpy as np
from hsvfilter import HsvFilter


class Vision:
    # constants
    TRACKBAR_WINDOW = "Trackbars"

    # Atributos
    object_img = None
    object_width = 0
    object_height = 0
    methods = None
    len_rect = 0

    def __init__(self, object_path):
        
        # Objeto a ser Encontrado.
        self.object_img = cv.imread(f"{object_path}")
        # Largura e Altura do objeto a ser procurado.
        self.object_width = self.object_img.shape[0]
        self.object_height = self.object_img.shape[1]
        self.methods = (cv.TM_CCOEFF_NORMED, cv.TM_CCORR_NORMED, cv.TM_SQDIFF_NORMED)


    def find(self, full_image, method=0, limite_max=0.5, max_results=10):

        # Irá mostrar os pontos que mais se parecem com o objeto que está procurando.
        results = cv.matchTemplate(full_image, self.object_img, self.methods[method])

        # min_val, max_val, min_loc, max_loc = cv.minMaxLoc(results)
        # print(max_val)

        limite = limite_max

        # Utiliza o método where da lib numpy que retorna uma matriz de locais (x, y) que estão maiores ou iguais ao limite definido.
        locations = np.where(results >= limite)
        # Inverte a matriz de locais de (y, x) => (x, y) e coloca todos as tuplas (x, y) em uma lista.
        locations = list(zip(*locations[::-1]))
        # print(len(locations))

        # Caso não encontre resultados, retorna um array vazio. esse reshape do array vazio
        # permite concatenar resultados sem causar um erro
        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)


        # Criar uma lista de retângulos [x, y, w, h]
        rectangles = []
        for loc in locations:
            rec = [int(loc[0]), int(loc[1]), self.object_width, self.object_height]
            rectangles.append(rec)
            rectangles.append(rec)

        # Agrupa todos os retangulos que estão na mesma posição em um único retângulo 
        rectangles, weights = cv.groupRectangles(rectangles, 1, 0.5)

        # Por razões de performance, retorna um número limitado de resultados.
        # Não são necessáriamente os melhores resultados.
        # if len(rectangles) > max_results:
        #     print("Warning! Muitos resultados, aumente o limite.")
        #     rectangles = rectangles[:max_results]

        return rectangles
    
    def get_click_postitions(self, rectangles):
        points = []

        for (x, y, w, h) in rectangles:
            # Determina a posição central.
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))

        # retorna o (x, y) do centro do objeto que estamos procurando.  
        return points
    
    def draw_rectangles(self, full_image, rectangles):

        # Precisei criar uma copy da full_image, pq estava dando erro. Não sei pq arrumou ao fazer isso.
        color_full_image = full_image.copy()

        line_color = (0, 255, 0)
        line_type = cv.LINE_4

        for (x, y, w, h) in rectangles:
        # Determina a posição e as informações do retângulo a ser desenhado
            top_left = (x, y)
            bottom_right = (top_left[0] + w, top_left[1] + h)

            cv.rectangle(color_full_image, top_left, bottom_right, color=line_color, thickness=2, lineType=line_type)

        return color_full_image
    
    def draw_crosshairs(self, full_image, points):

        # Precisei criar uma copy da full_image, pq estava dando erro. Não sei pq arrumou ao fazer isso.
        color_full_image = full_image.copy()

        marker_color = (0, 255, 0)
        marker_type = cv.MARKER_CROSS

        for (center_x, center_y) in points:
            cv.drawMarker(color_full_image, (center_x, center_y), marker_color, marker_type, thickness=2)
        
        return color_full_image

    def accuracy(self, full_image, method=0):
        # Retorna o valor máximo de precisão. 

        color_full_image = full_image.copy()

        full_image = cv.cvtColor(color_full_image)
        object_img = cv.cvtColor(self.object_img, )

        results = cv.matchTemplate(color_full_image, object_img, self.methods[method])

        max_val= cv.minMaxLoc(results)[1]

        return max_val
    
    def init_control_gui(self):
        cv.namedWindow(self.TRACKBAR_WINDOW, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.TRACKBAR_WINDOW, 350, 700)

        # Callback necessário. nós vamos utilizar o método getTrackbarPos() para fazer pesquisas.
        # ao invés de utilizar o callback.
        def nothing(position):
            pass

        # Cria uma trackbar para bracketing.
        # OpenCV scale for HSV is H: 0-179, S: 0-255, V: 0-255
        cv.createTrackbar('HMin', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar('SMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('HMax', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar('SMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        # Seta o valor default para as Max HSV trackbars
        cv.setTrackbarPos('HMax', self.TRACKBAR_WINDOW, 179)
        cv.setTrackbarPos('SMax', self.TRACKBAR_WINDOW, 255)
        cv.setTrackbarPos('VMax', self.TRACKBAR_WINDOW, 255)

        # trackbars para aumentar/diminuir value e saturation
        cv.createTrackbar('SAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('SSub', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VSub', self.TRACKBAR_WINDOW, 0, 255, nothing)

    # retorna um filtro HSV object baseado no controle da GUI
    def get_hsv_filter_from_controls(self):
        # Pega a posição atual de todas as trackbars.
        hsv_filter = HsvFilter()
        hsv_filter.hMin = cv.getTrackbarPos('HMin', self.TRACKBAR_WINDOW)
        hsv_filter.sMin = cv.getTrackbarPos('SMin', self.TRACKBAR_WINDOW)
        hsv_filter.vMin = cv.getTrackbarPos('VMin', self.TRACKBAR_WINDOW)
        hsv_filter.hMax = cv.getTrackbarPos('HMax', self.TRACKBAR_WINDOW)
        hsv_filter.sMax = cv.getTrackbarPos('SMax', self.TRACKBAR_WINDOW)
        hsv_filter.vMax = cv.getTrackbarPos('VMax', self.TRACKBAR_WINDOW)
        hsv_filter.sAdd = cv.getTrackbarPos('SAdd', self.TRACKBAR_WINDOW)
        hsv_filter.sSub = cv.getTrackbarPos('SSub', self.TRACKBAR_WINDOW)
        hsv_filter.vAdd = cv.getTrackbarPos('VAdd', self.TRACKBAR_WINDOW)
        hsv_filter.vSub = cv.getTrackbarPos('VSub', self.TRACKBAR_WINDOW)
        return hsv_filter
    
    # dado uma imagem e um filtro HSV, aplica o filtro e retorna a imagem processada
    # se um filtro não foi aplicado, então a trackbar GUI de controle vai ser usada
    def apply_hsv_filter(self, original_image, hsv_filter=None):
        # converte a imagem para HSV
        hsv = cv.cvtColor(original_image, cv.COLOR_BGR2HSV)

        # caso não tenha recebido um filtro HSV, utilizamos a trackbar GUI de controle
        if not hsv_filter:
            hsv_filter = self.get_hsv_filter_from_controls()

        # soma/subtrai saturation e value
        h, s, v = cv.split(hsv)
        s = self.shift_channel(s, hsv_filter.sAdd)
        s = self.shift_channel(s, -hsv_filter.sSub)
        v = self.shift_channel(v, hsv_filter.vAdd)
        v = self.shift_channel(v, -hsv_filter.vSub)
        hsv = cv.merge([h, s, v])

        # Seta os valores mínimo e máximo de HSV para exibição
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])
        # Aplica os limites
        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(hsv, hsv, mask=mask)

        # converte novamente para BGR para o método imshow() to display it properly
        img = cv.cvtColor(result, cv.COLOR_HSV2BGR)

        return img
    
    # apply adjustments to an HSV channel
    # https://stackoverflow.com/questions/49697363/shifting-hsv-pixel-values-in-python-using-numpy
    def shift_channel(self, c, amount):
        if amount > 0:
            lim = 255 - amount
            c[c >= lim] = 255
            c[c < lim] += amount
        elif amount < 0:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount
        return c