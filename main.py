from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.clock import mainthread

import threading
import trimesh
import os

# Configuração do fundo verde água
Window.clearcolor = (0.5, 0.9, 0.8, 1)  # RGBA

# Widget customizado para a caixa com fundo branco e bordas arredondadas
class RoundedBox(BoxLayout):
    def __init__(self, **kwargs):
        super(RoundedBox, self).__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Cor branca
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[20])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# Tela Principal
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Layout principal
        main_layout = BoxLayout(orientation='horizontal', padding=20, spacing=20)

        # Painel Esquerdo - Formulário
        form_layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint=(0.6, 1))

        # Título
        form_layout.add_widget(Label(text="[color=#004d40][b]Scanner[/b][/color]", markup=True, font_size=32))

        # Caixa arredondada com fundo branco
        rounded_box = RoundedBox(orientation='vertical', padding=20, spacing=15, size_hint=(1, None), height=400)

        # Campo de Nome
        rounded_box.add_widget(Label(text="Nome do Voluntário", color=(0.0, 0.3, 0.25, 1)))
        self.name_input = TextInput(hint_text="Nome do Voluntário", size_hint=(1, None), height=40)
        rounded_box.add_widget(self.name_input)

        # Campo de Idade
        rounded_box.add_widget(Label(text="Idade", color=(0.0, 0.3, 0.25, 1)))
        self.age_input = TextInput(hint_text="Idade", size_hint=(1, None), height=40)
        rounded_box.add_widget(self.age_input)

        # Campo de Altura
        rounded_box.add_widget(Label(text="Altura (cm)", color=(0.0, 0.3, 0.25, 1)))
        self.height_input = TextInput(hint_text="Altura (cm)", size_hint=(1, None), height=40)
        rounded_box.add_widget(self.height_input)

        # Campo de Peso
        rounded_box.add_widget(Label(text="Peso (gramas)", color=(0.0, 0.3, 0.25, 1)))
        self.weight_input = TextInput(hint_text="Peso (gramas)", size_hint=(1, None), height=40)
        rounded_box.add_widget(self.weight_input)

        # Campo de Etnia
        rounded_box.add_widget(Label(text="Etnia", color=(0.0, 0.3, 0.25, 1)))
        self.ethnic_input = TextInput(hint_text="Etnia", size_hint=(1, None), height=40)
        rounded_box.add_widget(self.ethnic_input)

        # Adiciona a caixa arredondada ao layout do formulário
        form_layout.add_widget(rounded_box)

        # Botão para selecionar o modelo 3D
        select_model_button = Button(
            text="Selecionar Modelo 3D",
            background_color=(0.3, 0.5, 0.4, 1),
            size_hint=(1, None),
            height=50
        )
        select_model_button.bind(on_press=self.load_mesh)
        form_layout.add_widget(select_model_button)

        # Botão de Ação
        action_button = Button(
            text="Calcular Gordura",
            background_color=(0.3, 0.5, 0.4, 1),
            size_hint=(1, None),
            height=50
        )
        action_button.bind(on_press=self.calc_fat)
        form_layout.add_widget(action_button)

        main_layout.add_widget(form_layout)

        # Painel Direito - Imagem ou Visualização
        view_layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint=(0.4, 1))
        self.volume_label = Label(text="Volume Sensor: *", font_size=18, color=(0.0, 0.3, 0.25, 1))
        view_layout.add_widget(self.volume_label)

        self.fat_label = Label(text="Percentual de Gordura: *", font_size=18, color=(0.0, 0.3, 0.25, 1))
        view_layout.add_widget(self.fat_label)

        main_layout.add_widget(view_layout)
        self.add_widget(main_layout)

    def calc_fat(self, instance):
        try:
            mesh_volume = float(self.mesh_volume)
            height = float(self.height_input.text)
            weight = float(self.weight_input.text)
            lung_volume = (((0.0472 * height) + (0.000009 * weight)) - 5.92) * 1000

            density = (weight / (mesh_volume - lung_volume))
            fat_percentage = max(0, (495 / density) - 450)  # Garantir que o percentual não seja negativo
            self.fat_label.text = f"Percentual de Gordura: {fat_percentage:.2f}%"
        except Exception as e:
            self.fat_label.text = f"Erro no cálculo: {str(e)}"

    def load_mesh(self, instance):
        content = BoxLayout(orientation='vertical')
        current_directory = os.getcwd()
        filechooser = FileChooserListView(path=current_directory, filters=["*.ply"])
        content.add_widget(filechooser)

        select_button = Button(text="Selecionar", size_hint=(1, 0.1))
        content.add_widget(select_button)

        popup = Popup(title="Selecione a malha", content=content, size_hint=(0.9, 0.9))

        def select_callback(instance):
            selection = filechooser.selection
            if selection:
                popup.dismiss()
                file_path = selection[0]
                threading.Thread(target=self.process_mesh, args=(file_path,)).start()

        select_button.bind(on_release=select_callback)
        popup.open()

    def process_mesh(self, file_path):
        try:
            mesh = trimesh.load(file_path)
            volume = mesh.volume / 1000.0  # Converter para litros
            self.update_volume_label(volume)
            self.mesh_volume = volume
        except Exception as e:
            self.update_volume_label(0)
            self.mesh_volume = 0
            self.fat_label.text = f"Erro ao carregar a malha: {str(e)}"

    @mainthread
    def update_volume_label(self, volume):
        self.volume_label.text = f"Volume Sensor: {volume:.2f} L"

class MyScreenManager(ScreenManager):
    pass

class MeuApp(App):
    def build(self):
        sm = MyScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    MeuApp().run()

