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

#include "central_widget.h"

/**
 * @brief Construct a new Central Widget object
 *
 * @param mw pointer to MainWindow object
 */
CentralWidget::CentralWidget(MainWindow* mw) {
    QHBoxLayout *layout = new QHBoxLayout;
    this->setLayout(layout);

    this->gl_widget = new GLWidget(this);
    this->gl_widget->setSizePolicy(QSizePolicy::Policy::Expanding, QSizePolicy::Policy::Expanding);
    layout->addWidget(this->gl_widget, 3);

    this->side_widget = new QStackedWidget(this);
    this->side_widget->setFrameShape(QFrame::NoFrame);
    layout->addWidget(this->side_widget, 1);

    this->symmetry_widget = new SymmetryWidget(this);
    side_widget->addWidget(this->symmetry_widget);

    this->practice_widget = new PracticeWidget(this);
    side_widget->addWidget(this->practice_widget);

    this->library = std::make_shared<Library>();

    this->practice_widget->set_library(this->library);

    connect(this->gl_widget, SIGNAL(animation_finished()), this->symmetry_widget, SLOT(request_operation()));
    connect(this->symmetry_widget, SIGNAL(animate_operation(Operation)), this->gl_widget, SLOT(start_animation(Operation)));
    connect(this->symmetry_widget, SIGNAL(operation_changed(bool, Operation)), this->gl_widget, SLOT(set_operation(bool, Operation)));
    connect(this->practice_widget, SIGNAL(request_new_structure()), mw, SLOT(load_library_practice_structure()));
    connect(this->practice_widget, SIGNAL(open_character_table_dialog()), mw, SLOT(open_character_table_dialog()));
    connect(this->practice_widget, SIGNAL(highlight_atoms(QList<unsigned int>)), this->gl_widget, SLOT(highlight_atoms(QList<unsigned int>)));
    connect(this->practice_widget, SIGNAL(label_atoms(QMap<unsigned int, std::string>)), this->gl_widget, SLOT(label_atoms(QMap<unsigned int, std::string>)));
}

/**
 * @brief Set the structure object
 *
 * @param structure
 */
void CentralWidget::set_structure(std::shared_ptr<Structure> structure) {
    this->structure = structure;
    auto symmetry = std::make_shared<Symmetry>(structure);
    this->symmetry = symmetry;
    this->symmetry_set = true;

    this->gl_widget->set_structure(structure, symmetry->get_cartesian_axes());

    this->symmetry_widget->set_symmetry(symmetry);
    this->practice_widget->create_practice_structure(symmetry);
}

void CentralWidget::set_gui_mode(QAction* action) {
    this->gui_mode = action->data().value<GuiMode>();

    int index;
    switch (this->gui_mode) {
        case GuiMode::SymmetryViewer:
            index = this->side_widget->indexOf(this->symmetry_widget);
            break;
        case GuiMode::Practice:
            index = this->side_widget->indexOf(this->practice_widget);
            break;
        default:
            throw std::runtime_error("Unexpected GUI mode encountered.");
    }
    this->side_widget->setCurrentIndex(index);
}

/**
 * @brief Get the GL widget object
 *
 * @return GLWidget*
 */
GLWidget* CentralWidget::get_gl_widget() {
    return this->gl_widget;
}

/**
 * @brief Get whether the symmetry object is set
 *
 * @return true
 * @return false
 */
bool CentralWidget::get_symmetry_set() {
    return this->symmetry_set;
}

/**
 * @brief Get the symmetry object
 *
 * @return std::shared_ptr<Symmetry>&
 */
std::shared_ptr<Symmetry>& CentralWidget::get_symmetry() {
    return this->symmetry;
}

/**
 * @brief Get the library object
 *
 * @return std::shared_ptr<Library>&
 */
std::shared_ptr<Library>& CentralWidget::get_library() {
    return this->library;
}
