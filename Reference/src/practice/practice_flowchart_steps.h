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

#ifndef PRACTICE_PRACTICE_FLOWCHART_STEPS_H
#define PRACTICE_PRACTICE_FLOWCHART_STEPS_H

#include <stdexcept>
#include <string>
#include <unordered_map>
#include "../symmetry/operations/operation.h"
#include "../symmetry/operations/operation_label.h"
#include "../symmetry/point_groups/point_group_label.h"
#include "../symmetry/rotor_class.h"
#include "practice_flowchart_step.h"

typedef PointGroupLabel::Class Class;
typedef PracticeFlowchartStep::Type Type;

class PracticeFlowchartSteps final {
private:
    /**
     * @brief Mapping from step key to step object
     */
    static const std::unordered_map<std::string, PracticeFlowchartStep> steps;

public:
    /**
     * @brief Step key of first step
     */
    static const std::string first_step;

    /**
     * @brief Get the step object from a key
     *
     * @param key step key
     * @return PracticeFlowchartStep step object
     */
    static PracticeFlowchartStep get_step(const std::string key);

private:
    /**
     * @brief Default constructor
     */
    PracticeFlowchartSteps() {}
};

#endif  // PRACTICE_PRACTICE_FLOWCHART_STEPS_H
