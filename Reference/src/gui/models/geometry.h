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

#ifndef GUI_MODELS_GEOMETRY_H
#define GUI_MODELS_GEOMETRY_H

#include <cmath>
#include <math.h>
#include <memory>
#include <vector>
#include <glm/glm.hpp>
#include "model_2d.h"
#include "model_3d.h"

class Geometry final {
public:
    /**
     * @brief Create a unique pointer to a sphere model
     *
     * @param tesselation_level detail of the sphere
     * @return std::unique_ptr<Model3D>
     */
    static std::unique_ptr<Model3D> sphere(unsigned int tesselation_level = 3);

    /**
     * @brief Create a unique pointer to a cylinder model
     *
     * @param include_caps whether to include cylinder caps
     * @param stack_count number of stacks in axial direction
     * @param slice_count number of slices in radial direction
     * @return std::unique_ptr<Model3D>
     */
    static std::unique_ptr<Model3D> cylinder(bool include_caps = false, unsigned int stack_count = 2, unsigned int slice_count = 24);

        /**
     * @brief Create a unique pointer to a circle model
     *
     * @param slice_count number of slices
     * @return std::unique_ptr<Model3D>
     */
    static std::unique_ptr<Model3D> circle(unsigned int slice_count = 96);

    /**
     * @brief Create a unique pointer to a quad model
     *
     * @return std::unique_ptr<Model2D>
     */
    static std::unique_ptr<Model2D> quad();

    /**
     * @brief Create a unique pointer to a 3D quad model
     *
     * @return std::unique_ptr<Model3D>
     */
    static std::unique_ptr<Model3D> quad_3d();
};

#endif  // GUI_MODELS_GEOMETRY_H
