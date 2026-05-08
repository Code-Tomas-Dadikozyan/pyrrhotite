/**
 * Schoenflies
 * Copyright (c) 2021 Luuk Kempen
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include "main_window.h"

/**
 * @brief Construct a new Main Window object
 */
MainWindow::MainWindow() {
    this->setWindowTitle(QString(PROGRAM_NAME));
    this->setWindowIcon(QIcon(":/assets/icons/schoenflies.ico"));

    // central widget
    this->central_widget = new CentralWidget(this);
    setCentralWidget(this->central_widget);

    // menu bar
    QMenuBar *menu_bar = new QMenuBar;

    // drop-down menus
    QMenu *menu_file = menu_bar->addMenu(tr("&File"));
    QMenu *menu_stereoscopy = menu_bar->addMenu(tr("&Stereoscopy"));
    QMenu *menu_view = menu_bar->addMenu(tr("&View"));
    QMenu *menu_help = menu_bar->addMenu(tr("&Help"));

    // actions for file menu
    QAction *action_open = new QAction(menu_file);
    action_open->setText(tr("Open"));
    action_open->setShortcuts(QKeySequence::Open);
    connect(action_open, &QAction::triggered, this, &MainWindow::open);
    menu_file->addAction(action_open);

    QAction *action_open_library = new QAction(menu_file);
    action_open_library->setText(tr("Open from library"));
    action_open_library->setShortcut(QKeySequence(Qt::CTRL | Qt::ALT + Qt::Key_O));
    connect(action_open_library, &QAction::triggered, this, &MainWindow::open_library_dialog);
    menu_file->addAction(action_open_library);

    QAction *action_exit = new QAction(menu_file);
    action_exit->setText(tr("Exit"));
    action_exit->setShortcuts(QKeySequence::Quit);
    connect(action_exit, &QAction::triggered, this, &MainWindow::exit);
    menu_file->addAction(action_exit);

    // actions for stereoscopy menu
    QAction *action_two_dimensional = new QAction(menu_stereoscopy);
    action_two_dimensional->setCheckable(true);
    action_two_dimensional->setChecked(true);
    action_two_dimensional->setText(tr("Two-dimensional (off)"));
    action_two_dimensional->setData(StereoscopicMethod::None);
    menu_stereoscopy->addAction(action_two_dimensional);

    QAction *action_anaglyph_red_cyan = new QAction(menu_stereoscopy);
    action_anaglyph_red_cyan->setCheckable(true);
    action_anaglyph_red_cyan->setText(tr("Anaglyph (red/cyan)"));
    action_anaglyph_red_cyan->setData(StereoscopicMethod::AnaglyphRedCyan);
    menu_stereoscopy->addAction(action_anaglyph_red_cyan);

    QAction *action_interlaced_rows_lr = new QAction(menu_stereoscopy);
    action_interlaced_rows_lr->setCheckable(true);
    action_interlaced_rows_lr->setText(tr("Interlaced rows (left first)"));
    action_interlaced_rows_lr->setData(StereoscopicMethod::InterlacedRowsLR);
    menu_stereoscopy->addAction(action_interlaced_rows_lr);

    QAction *action_interlaced_rows_rl = new QAction(menu_stereoscopy);
    action_interlaced_rows_rl->setCheckable(true);
    action_interlaced_rows_rl->setText(tr("Interlaced rows (right first)"));
    action_interlaced_rows_rl->setData(StereoscopicMethod::InterlacedRowsRL);
    menu_stereoscopy->addAction(action_interlaced_rows_rl);

    QAction *action_interlaced_columns_lr = new QAction(menu_stereoscopy);
    action_interlaced_columns_lr->setCheckable(true);
    action_interlaced_columns_lr->setText(tr("Interlaced columns (left first)"));
    action_interlaced_columns_lr->setData(StereoscopicMethod::InterlacedColumnsLR);
    menu_stereoscopy->addAction(action_interlaced_columns_lr);

    QAction *action_interlaced_columns_rl = new QAction(menu_stereoscopy);
    action_interlaced_columns_rl->setCheckable(true);
    action_interlaced_columns_rl->setText(tr("Interlaced columns (right first)"));
    action_interlaced_columns_rl->setData(StereoscopicMethod::InterlacedColumnsRL);
    menu_stereoscopy->addAction(action_interlaced_columns_rl);

    QAction *action_interlaced_checkerboard_lr = new QAction(menu_stereoscopy);
    action_interlaced_checkerboard_lr->setCheckable(true);
    action_interlaced_checkerboard_lr->setText(tr("Interlaced checkerboard (left first)"));
    action_interlaced_checkerboard_lr->setData(StereoscopicMethod::InterlacedCheckerboardLR);
    menu_stereoscopy->addAction(action_interlaced_checkerboard_lr);

    QAction *action_interlaced_checkerboard_rl = new QAction(menu_stereoscopy);
    action_interlaced_checkerboard_rl->setCheckable(true);
    action_interlaced_checkerboard_rl->setText(tr("Interlaced checkerboard (right first)"));
    action_interlaced_checkerboard_rl->setData(StereoscopicMethod::InterlacedCheckerboardRL);
    menu_stereoscopy->addAction(action_interlaced_checkerboard_rl);

    QActionGroup *action_group_stereoscopy = new QActionGroup(this);
    action_group_stereoscopy->addAction(action_two_dimensional);
    action_group_stereoscopy->addAction(action_anaglyph_red_cyan);
    action_group_stereoscopy->addAction(action_interlaced_rows_lr);
    action_group_stereoscopy->addAction(action_interlaced_rows_rl);
    action_group_stereoscopy->addAction(action_interlaced_columns_lr);
    action_group_stereoscopy->addAction(action_interlaced_columns_rl);
    action_group_stereoscopy->addAction(action_interlaced_checkerboard_lr);
    action_group_stereoscopy->addAction(action_interlaced_checkerboard_rl);
    connect(action_group_stereoscopy, &QActionGroup::triggered, this->central_widget->get_gl_widget(), &GLWidget::set_stereoscopic_method);

    // actions for view menu
    QAction *action_viewer = new QAction(menu_view);
    action_viewer->setCheckable(true);
    action_viewer->setChecked(true);
    action_viewer->setText(tr("Symmetry viewer"));
    action_viewer->setData(GuiMode::SymmetryViewer);
    menu_view->addAction(action_viewer);

    QAction *action_practice = new QAction(menu_view);
    action_practice->setCheckable(true);
    action_practice->setText(tr("Practice"));
    action_practice->setData(GuiMode::Practice);
    menu_view->addAction(action_practice);

    QActionGroup *action_group_mode = new QActionGroup(this);
    action_group_mode->addAction(action_viewer);
    action_group_mode->addAction(action_practice);
    connect(action_group_mode, &QActionGroup::triggered, this->central_widget, &CentralWidget::set_gui_mode);

    menu_view->addSeparator();

    QAction *action_open_character_table = new QAction(menu_view);
    action_open_character_table->setText(tr("Character tables"));
    action_open_character_table->setShortcut(QKeySequence(Qt::CTRL | Qt::ALT + Qt::Key_T));
    connect(action_open_character_table, &QAction::triggered, this, &MainWindow::open_character_table_dialog);
    menu_view->addAction(action_open_character_table);

    menu_view->addSeparator();

    QAction *action_show_default_labels = new QAction(menu_view);
    action_show_default_labels->setCheckable(true);
    action_show_default_labels->setText(tr("Show atom labels"));
    menu_view->addAction(action_show_default_labels);
    connect(action_show_default_labels, &QAction::triggered, this->central_widget->get_gl_widget()->get_structure_renderer().get(), &StructureRenderer::set_default_labels_visible);

    // actions for help menu
    QAction *action_about = new QAction(menu_help);
    action_about->setText(tr("About"));
    connect(action_about, &QAction::triggered, this, &MainWindow::about);
    menu_help->addAction(action_about);

    setMenuBar(menu_bar);

    // status bar
    statusBar()->showMessage(PROGRAM_NAME);
}

/**
 * @brief Handle window move event
 *
 * @param event
 */
void MainWindow::moveEvent(QMoveEvent* event) {
    this->central_widget->get_gl_widget()->window_move_event();
}

/**
 * @brief Load a structure
 *
 * @param filename
 */
void MainWindow::load_structure(const std::string& filename) {
    auto structure = std::make_shared<Structure>(filename);
    statusBar()->showMessage(QString::fromStdString(structure->get_description_filename()));
    this->central_widget->set_structure(structure);
}

/**
 * @brief Load a structure
 *
 * @param item
 */
void MainWindow::load_structure(const LibraryItem& item) {
    auto structure = std::make_shared<Structure>(item.get_path());
    structure->set_library_item(std::make_shared<LibraryItem>(item));
    statusBar()->showMessage(QString::fromStdString(structure->get_description_filename()));
    this->central_widget->set_structure(structure);
}

/**
 * @brief Open a new file
 */
void MainWindow::open() {
    std::string filename = QFileDialog::getOpenFileName(this, tr("Open file"), "", tr("All supported files (*.xyz);;xyz file (*.xyz)")).toStdString();
    if (filename.empty()) return;

    this->load_structure(filename);
}

/**
 * @brief Open the library dialog
 */
void MainWindow::open_library_dialog() {
    this->library_dialog = new LibraryDialog(this);
    this->library_dialog->set_library(this->central_widget->get_library());
    this->library_dialog->open();
}

/**
 * @brief Handle the return value of the library dialog
 *
 * @param result dialog result code
 */
void MainWindow::handle_library_dialog(int result) {
    if (result == QDialog::DialogCode::Accepted) {
        const std::string& filename = this->library_dialog->get_selected_item_path();
        if (filename.empty()) return;

        this->load_structure(filename);
    }
}

/**
 * @brief Load a random practice structure from the library
 */
void MainWindow::load_library_practice_structure() {
    LibraryItem& item = this->central_widget->get_library()->get_practice_item();
    this->load_structure(item);
}

/**
 * @brief Open the character table dialog
 */
void MainWindow::open_character_table_dialog() {
    if (this->character_table_dialog == nullptr || !this->character_table_dialog->isVisible()) {
        this->character_table_dialog = new CharacterTableDialog(this);
        this->character_table_dialog->show();
    }
    if (this->central_widget->get_symmetry_set()) {
        this->character_table_dialog->show_point_group(
            this->central_widget->get_symmetry()->get_point_group().get_label());
    }
}

/**
 * @brief Close the application
 */
void MainWindow::exit() {
    QApplication::quit();
}

/**
 * @brief Display about menu
 */
void MainWindow::about() {
    QMessageBox message_box;
    message_box.setText(PROGRAM_NAME ": " PROGRAM_DESC ", version " PROGRAM_VERSION "\n"
                        "Copyright (c) 2021 Luuk Kempen\n"
                        PROGRAM_NAME " is licensed under the GPLv3 license.\n"
                        PROGRAM_NAME " is partially funded by the BOOST! program "
                        "of Eindhoven University of Technology (https://boost.tue.nl).");
    message_box.setWindowTitle("About " PROGRAM_NAME);
    message_box.setWindowIcon(QIcon(":/assets/icons/schoenflies.ico"));
    message_box.exec();
}
