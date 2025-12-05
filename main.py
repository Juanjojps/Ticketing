import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtUiTools import QUiLoader
from datetime import datetime
import os

# Evitar conflicto con plugins de otros proyectos (ej: TimeControl)
if "PYSIDE_DESIGNER_PLUGINS" in os.environ:
    del os.environ["PYSIDE_DESIGNER_PLUGINS"]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Cargar la interfaz .ui
        loader = QUiLoader()
        # Asegurarse de que la ruta es correcta
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "ui", "incidencias.ui")
        
        ui_file = QtCore.QFile(ui_path)
        if not ui_file.open(QtCore.QFile.ReadOnly):
            print(f"Error: No se pudo abrir {ui_path}")
            sys.exit(-1)
            
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        if not self.ui:
            print(f"Error: {loader.errorString()}")
            sys.exit(-1)

        # Si el archivo .ui es un QMainWindow, extraemos su central widget
        if isinstance(self.ui, QMainWindow):
             cw = self.ui.centralWidget()
             if cw:
                 self.setCentralWidget(cw)
             else:
                 self.setCentralWidget(self.ui)
        else:
             self.setCentralWidget(self.ui)

        self.setWindowTitle("Gestión de Incidencias")

        # Lista principal de incidencias (modelo en memoria)
        self.incidencias = []   # cada incidencia será un dict
        self.tema_oscuro = False

        # Configuración inicial
        self._configurar_tabla()
        self._conectar_signals()
        
        # Inicializar fecha del formulario a hoy
        self.ui.dateFecha.setDate(QtCore.QDate.currentDate())
        
        self._actualizar_dashboard()
        self._log("Aplicación iniciada")

    def _configurar_tabla(self):
        tabla = self.ui.tablaIncidencias
        tabla.setColumnCount(6)
        tabla.setHorizontalHeaderLabels(
            ["ID", "Título", "Cliente", "Estado", "Prioridad", "Fecha"]
        )
        tabla.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        tabla.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        # Ajustar ancho de columnas
        header = tabla.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def _conectar_signals(self):
        self.ui.btnNuevaIncidencia.clicked.connect(self.crear_incidencia)
        self.ui.btnActualizarIncidencia.clicked.connect(self.actualizar_incidencia)
        self.ui.btnEliminarIncidencia.clicked.connect(self.eliminar_incidencia)

        self.ui.btnAplicarFiltros.clicked.connect(self.aplicar_filtros)
        self.ui.btnLimpiarFiltros.clicked.connect(self.limpiar_filtros)

        self.ui.btnTema.clicked.connect(self.cambiar_tema)

        # Doble click en la tabla para cargar datos en el formulario
        self.ui.tablaIncidencias.cellDoubleClicked.connect(self.cargar_incidencia_form)

    def crear_incidencia(self):
        titulo = self.ui.txtTitulo.text().strip()
        cliente = self.ui.txtCliente.text().strip()
        descripcion = self.ui.txtDescripcion.toPlainText().strip()
        estado = self.ui.cmbEstado.currentText()
        prioridad = self.ui.cmbPrioridad.currentText()
        fecha_qdate = self.ui.dateFecha.date()
        fecha_str = fecha_qdate.toString("yyyy-MM-dd")

        # 1) Validación mínima
        if not titulo or not cliente:
            QMessageBox.warning(self, "Datos incompletos", "Título y cliente son obligatorios.")
            return

        # 2) Calcular ID (ej: siguiente número)
        if self.incidencias:
            nuevo_id = max(i["id"] for i in self.incidencias) + 1
        else:
            nuevo_id = 1

        # 3) Crear diccionario
        nueva = {
            "id": nuevo_id,
            "titulo": titulo,
            "cliente": cliente,
            "descripcion": descripcion,
            "estado": estado,
            "prioridad": prioridad,
            "fecha": fecha_str
        }

        # 4) Añadir a la lista
        self.incidencias.append(nueva)

        # 5) Refrescar tabla y dashboard
        # Si hay filtros aplicados, quizás deberíamos limpiarlos o reaplicarlos. 
        # Por simplicidad, limpiamos filtros para ver la nueva incidencia.
        self.limpiar_filtros() 
        self._actualizar_dashboard()

        # 6) Limpiar formulario
        self.ui.txtTitulo.clear()
        self.ui.txtCliente.clear()
        self.ui.txtDescripcion.clear()
        self.ui.cmbEstado.setCurrentIndex(0)
        self.ui.cmbPrioridad.setCurrentIndex(0)
        self.ui.dateFecha.setDate(QtCore.QDate.currentDate())

        # 7) Log
        self._log(f"Creada incidencia #{nuevo_id}: {titulo}")

    def actualizar_incidencia(self):
        tabla = self.ui.tablaIncidencias
        fila = tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Sin selección", "Selecciona una incidencia en la tabla para actualizar.")
            return

        id_item = tabla.item(fila, 0)
        if not id_item:
            return
        id_incidencia = int(id_item.text())

        # Buscar la incidencia en self.incidencias
        inc = next((i for i in self.incidencias if i["id"] == id_incidencia), None)
        if not inc:
            return

        # Leer datos del formulario
        titulo = self.ui.txtTitulo.text().strip()
        cliente = self.ui.txtCliente.text().strip()
        
        if not titulo or not cliente:
             QMessageBox.warning(self, "Datos incompletos", "Título y cliente son obligatorios para actualizar.")
             return

        # Actualizar los campos
        inc["titulo"] = titulo
        inc["cliente"] = cliente
        inc["descripcion"] = self.ui.txtDescripcion.toPlainText().strip()
        inc["estado"] = self.ui.cmbEstado.currentText()
        inc["prioridad"] = self.ui.cmbPrioridad.currentText()
        inc["fecha"] = self.ui.dateFecha.date().toString("yyyy-MM-dd")

        # Refrescar tabla (manteniendo filtros si los hubiera, pero aquí refrescamos todo por simplicidad)
        # O idealmente, llamar a aplicar_filtros() para refrescar la vista actual
        self.aplicar_filtros() 
        self._actualizar_dashboard()
        
        self._log(f"Actualizada incidencia #{id_incidencia}")

    def eliminar_incidencia(self):
        tabla = self.ui.tablaIncidencias
        fila = tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Sin selección", "Selecciona una incidencia en la tabla para eliminar.")
            return

        id_item = tabla.item(fila, 0)
        if not id_item:
            return
        id_incidencia = int(id_item.text())

        respuesta = QMessageBox.question(
            self, 
            "Confirmar eliminación", 
            f"¿Estás seguro de eliminar la incidencia #{id_incidencia}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            self.incidencias = [i for i in self.incidencias if i["id"] != id_incidencia]
            self.aplicar_filtros() # Refrescar vista
            self._actualizar_dashboard()
            self._log(f"Eliminada incidencia #{id_incidencia}")
            
            # Limpiar formulario si era la que estaba cargada (opcional, pero buena UX)
            self.ui.txtTitulo.clear()
            self.ui.txtCliente.clear()
            self.ui.txtDescripcion.clear()

    def aplicar_filtros(self):
        texto = self.ui.txtFiltroTexto.text().strip().lower()
        estado_filtro = self.ui.cmbFiltroEstado.currentText()
        prioridad_filtro = self.ui.cmbFiltroPrioridad.currentText()

        resultado = []
        for inc in self.incidencias:
            # Comprobar texto en título/cliente
            if texto:
                if texto not in inc["titulo"].lower() and texto not in inc["cliente"].lower():
                    continue

            # Comprobar estado (si no es "Todos")
            if estado_filtro != "Todos" and inc["estado"] != estado_filtro:
                continue

            # Comprobar prioridad (si no es "Todas")
            if prioridad_filtro != "Todas" and inc["prioridad"] != prioridad_filtro:
                continue

            resultado.append(inc)

        self._actualizar_tabla(resultado)
        # No logueamos cada vez que se filtra para no saturar, o sí, según gusto.
        # self._log(f"Filtros aplicados. Resultados: {len(resultado)}")

    def limpiar_filtros(self):
        self.ui.txtFiltroTexto.clear()
        self.ui.cmbFiltroEstado.setCurrentIndex(0)   # "Todos"
        self.ui.cmbFiltroPrioridad.setCurrentIndex(0) # "Todas"
        self._actualizar_tabla()
        self._log("Filtros limpiados")

    def cargar_incidencia_form(self, fila, columna):
        tabla = self.ui.tablaIncidencias
        id_item = tabla.item(fila, 0)

        if not id_item:
            return

        id_incidencia = int(id_item.text())

        # Buscar incidencia por ID
        inc = next((i for i in self.incidencias if i["id"] == id_incidencia), None)
        if not inc:
            return

        # Cargar en el formulario
        self.ui.txtTitulo.setText(inc["titulo"])
        self.ui.txtCliente.setText(inc["cliente"])
        self.ui.txtDescripcion.setPlainText(inc["descripcion"])
        self.ui.cmbEstado.setCurrentText(inc["estado"])
        self.ui.cmbPrioridad.setCurrentText(inc["prioridad"])

        # Fecha
        fecha = QtCore.QDate.fromString(inc["fecha"], "yyyy-MM-dd")
        self.ui.dateFecha.setDate(fecha)
        
        self._log(f"Cargada incidencia #{id_incidencia} en formulario")

    def _actualizar_tabla(self, incidencias_mostrar=None):
        if incidencias_mostrar is None:
            incidencias_mostrar = self.incidencias

        tabla = self.ui.tablaIncidencias
        tabla.setRowCount(len(incidencias_mostrar))

        for fila, inc in enumerate(incidencias_mostrar):
            tabla.setItem(fila, 0, QTableWidgetItem(str(inc["id"])))
            tabla.setItem(fila, 1, QTableWidgetItem(inc["titulo"]))
            tabla.setItem(fila, 2, QTableWidgetItem(inc["cliente"]))
            tabla.setItem(fila, 3, QTableWidgetItem(inc["estado"]))
            tabla.setItem(fila, 4, QTableWidgetItem(inc["prioridad"]))
            tabla.setItem(fila, 5, QTableWidgetItem(inc["fecha"]))

        # tabla.resizeColumnsToContents() # A veces es mejor dejar que el header stretch haga su trabajo

    def _actualizar_dashboard(self):
        total = len(self.incidencias)
        abiertas = sum(1 for i in self.incidencias if i["estado"] == "Abierta")
        en_curso = sum(1 for i in self.incidencias if i["estado"] == "En curso")
        cerradas = sum(1 for i in self.incidencias if i["estado"] == "Cerrada")

        alta = sum(1 for i in self.incidencias if i["prioridad"] == "Alta")
        media = sum(1 for i in self.incidencias if i["prioridad"] == "Media")
        baja = sum(1 for i in self.incidencias if i["prioridad"] == "Baja")

        self.ui.lblTotalIncidencias.setText(f"Total: {total}")
        self.ui.lblAbiertas.setText(f"Abiertas: {abiertas}")
        self.ui.lblEnCurso.setText(f"En curso: {en_curso}")
        self.ui.lblCerradas.setText(f"Cerradas: {cerradas}")
        self.ui.lblAlta.setText(f"Alta: {alta}")
        self.ui.lblMedia.setText(f"Media: {media}")
        self.ui.lblBaja.setText(f"Baja: {baja}")

    def cambiar_tema(self):
        if self.tema_oscuro:
            # Pasar a claro
            self.tema_oscuro = False
            self.ui.lblTemaActual.setText("Tema: claro")
            self.setStyleSheet("")   # sin estilos = por defecto
            self._log("Cambiado a tema claro")
        else:
            # Pasar a oscuro (un estilo sencillo)
            self.tema_oscuro = True
            self.ui.lblTemaActual.setText("Tema: oscuro")
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; }
                QWidget { color: #ffffff; background-color: #2b2b2b; }
                QLineEdit, QTextEdit, QComboBox, QTableWidget, QDateEdit {
                    background-color: #3c3f41;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QHeaderView::section {
                    background-color: #3c3f41;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #555555;
                    color: #ffffff;
                    border-radius: 4px;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 3px;
                }
            """)
            self._log("Cambiado a tema oscuro")

    def _log(self, mensaje):
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{ahora}] {mensaje}"
        self.ui.txtLog.append(linea)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())
