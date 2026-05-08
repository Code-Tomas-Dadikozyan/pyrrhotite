/**
 * Schoenflies
 * Copyright (c) 2022 Luuk Kempen
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

#ifndef GUI_PRACTICE_PROJECTION_WIDGET_H
#define GUI_PRACTICE_PROJECTION_WIDGET_H

#include <algorithm>
#include <iterator>
#include <string>
#include <vector>
#include <Qt>
#include <QButtonGroup>
#include <QDoubleValidator>
#include <QGridLayout>
#include <QLabel>
#include <QLineEdit>
#include <QMap>
#include <QPushButton>
#include <QScrollArea>
#include <QScrollBar>
#include <QVBoxLayout>
#include <QWidget>
#include "../practice/practice_projection.h"
#include "../practice/practice_structure.h"

class PracticeProjectionWidget: public QScrollArea {
    Q_OBJECT

private:
    QVBoxLayout *layout;
    QWidget *container;

    QLabel *question;

    QVBoxLayout *grid_layout;
    std::vector<QWidget*> grid_containers;
    std::vector<QGridLayout*> grids;
    QButtonGroup *button_group;
    std::vector<QPushButton*> buttons;

    PracticeProjection projection;

public:
    /**
     * @brief Construct a new PracticeProjectionWidget object
     *
     * @param parent pointer to parent widget
     */
    PracticeProjectionWidget(QWidget* parent);

    /**
     * @brief Initialize a new exercise
     *
     * @param practice_structure
     */
    void initialize(std::shared_ptr<PracticeStructure> practice_structure);

private:
    /**
     * @brief Show the correct answers
     */
    void show_answers();

private slots:
    /**
     * @brief Scroll the widget to the bottom
     */
    void scroll_to_bottom();

    /**
     * @brief Show the next part of the exercise
     *
     * @param id button id
     */
    void show_next(int id);

signals:
    /**
     * @brief Emitted when the user has finished the exercise
     */
    void finished_exercise();

    /**
     * @brief Highlight atoms in the GL widget
     *
     * @param atoms atom indices to highlight
     */
    void highlight_atoms(const QList<unsigned int>& atoms);

    /**
     * @brief Label atoms in the GL widget
     *
     * @param labels map of atom indices and labels
     */
    void label_atoms(const QMap<unsigned int, std::string>& labels);
};

#endif  // GUI_PRACTICE_PROJECTION_WIDGET_H
