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

#ifndef GUI_PRACTICE_CONFIG_WIDGET_H
#define GUI_PRACTICE_CONFIG_WIDGET_H

#include <memory>
#include <QCheckBox>
#include <QLabel>
#include <QPushButton>
#include <QScrollArea>
#include <QVBoxLayout>
#include <QWidget>
#include "../practice/practice_config.h"
#include "../practice/practice_module.h"

class PracticeConfigWidget: public QScrollArea {
    Q_OBJECT

private:
    QVBoxLayout *layout;
    QWidget *container;

    QCheckBox *flowchart_checkbox;
    QCheckBox *irreps_checkbox;
    QCheckBox *projection_checkbox;
    QPushButton *start_button;

    std::shared_ptr<PracticeConfig> practice_config;

public:
    /**
     * @brief Construct a new PracticeConfigWidget object
     *
     * @param parent pointer to parent widget
     */
    PracticeConfigWidget(QWidget* parent);

    /**
     * @brief Get the practice configuration object
     *
     * @return std::shared_ptr<PracticeConfig>&
     */
    std::shared_ptr<PracticeConfig>& get_practice_config();

private slots:
    /**
     * @brief Create the configuration object based on the user's input
     */
    void create_practice_config();

signals:
    /**
     * @brief Emitted when the user starts practice
     */
    void start();
};

#endif  // GUI_PRACTICE_CONFIG_WIDGET_H
