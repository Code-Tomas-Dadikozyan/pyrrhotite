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

#ifndef PRACTICE_PRACTICE_FLOWCHART_H
#define PRACTICE_PRACTICE_FLOWCHART_H

#include <iostream>

#include <algorithm>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include "practice_flowchart_step.h"
#include "practice_flowchart_steps.h"
#include "practice_structure.h"

class PracticeFlowchart {
private:
public:
    std::shared_ptr<PracticeStructure> practice_structure;
    std::vector<std::shared_ptr<PracticeFlowchartStep>> steps_taken;

    int n = 0;

public:
    /**
     * @brief Default constructor
     */
    PracticeFlowchart();

    /**
     * @brief Construct a new Practice Flowchart object
     *
     * @param practice_structure practice structure object
     */
    PracticeFlowchart(std::shared_ptr<PracticeStructure> practice_structure);

    /**
     * @brief Handle an answer given to a step
     *
     * @param step_index step index
     * @param answer given answer
     * @return bool if anything was changed
     */
    bool handle_answer(int step_index, int answer);

    /**
     * @brief Get a step by index
     *
     * @param step_index step index
     * @return std::shared_ptr<PracticeFlowchartStep>
     */
    std::shared_ptr<PracticeFlowchartStep> get_step(int step_index);

    /**
     * @brief Get the index of the latest step
     *
     * @return unsigned int
     */
    unsigned int get_latest_step_index();

private:
    /**
     * @brief Add a step to the flowchart by key
     *
     * @param key
     */
    void add_step(std::string key);
};

#endif  // PRACTICE_PRACTICE_FLOWCHART_H
