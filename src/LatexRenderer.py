from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PyQt6.QtGui import QImage, QPixmap
import io
import threading

# Lock global para isolar operações de renderização
renderer_lock = threading.Lock()

class LatexRenderer:
    @staticmethod
    def render(latex_str, font_size=20, color='#5090d0'):
        # MUITO IMPORTANTE: Usar a API Orientada a Objetos do Matplotlib (Figure)
        # em vez da funcional (pyplot/plt) evita conflitos de backend com o Qt.
        with renderer_lock:
            latex_str = latex_str.strip()
            if not latex_str.startswith('$'):
                latex_str = f"${latex_str}$"
                
            try:
                # Cria a figura diretamente sem usar o pyplot global
                fig = Figure(figsize=(0.1, 0.1), dpi=200)
                fig.patch.set_alpha(0)
                canvas = FigureCanvasAgg(fig)
                
                # Renderiza o texto no objeto Figure
                text_obj = fig.text(
                    0, 0, latex_str, 
                    fontsize=font_size, 
                    color=color,
                    ha='left', va='bottom'
                )
                
                # Força o cálculo do layout
                canvas.draw()
                
                # Obtém o tamanho real em pixels
                bbox = text_obj.get_window_extent(canvas.get_renderer())
                width, height = bbox.width, bbox.height
                
                # Ajusta e salva em memória
                fig.set_size_inches(width/200, height/200)
                buf = io.BytesIO()
                fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0.05)
                
                buf.seek(0)
                img_data = buf.read()
                
                qimage = QImage.fromData(img_data)
                return QPixmap.fromImage(qimage)
                
            except Exception as e:
                print(f"CRITICAL RENDER ERROR: {e}")
                # Fallback: Retorna um pequeno pixmap transparente
                fallback = QPixmap(1, 1)
                fallback.fill(Qt.GlobalColor.transparent)
                return fallback
            finally:
                # Garante limpeza manual se necessário (embora Figure não precise de plt.close)
                del fig
