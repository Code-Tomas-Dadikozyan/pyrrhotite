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

#ifndef STRUCTURE_RENDERER_H
#define STRUCTURE_RENDERER_H

#include <chrono>
#include <cmath>
#include <math.h>
#include <memory>
#include <numeric>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <QObject>
#include "gui/models/model_instance.h"
#include "gui/text/character.h"
#include "gui/text/freetype_font.h"
#include "periodic_table/element.h"
#include "periodic_table/periodic_table.h"
#include "symmetry/operations/operation.h"
#include "symmetry/operations/operation_label.h"
#include "structure.h"

class StructureRenderer: public QObject {
    Q_OBJECT

private:
    bool structure_set;

    glm::mat4x4 camera_rotation;
    glm::mat4x4 arcball_rotation;

    std::shared_ptr<Structure> structure;
    glm::mat4x4 structure_rotation;
    glm::mat3x3 animation_matrix;

    std::vector<std::pair<unsigned int, unsigned int>> bond_pairs;

    float structure_span = 0;

    bool operation_set;
    Operation operation;

    bool animating;
    std::chrono::time_point<std::chrono::high_resolution_clock> animation_start_time;

    std::vector<unsigned int> animated_indices;
    std::unordered_set<unsigned int> highlighted_atoms;

    bool default_labels_visible = false;
    std::vector<std::string> default_labels;

    std::unordered_map<unsigned int, std::string> custom_labels;

    std::shared_ptr<FreeTypeFont> freetype_font;

public:
    /**
     * @brief Default constructor
     *
     * @param freetype_font
     */
    StructureRenderer(const std::shared_ptr<FreeTypeFont> freetype_font);

    /**
     * @brief Set the structure
     *
     * @param structure structure to render from
     * @param cartesian_axes matrix of unit vectors along which the Cartesian
     * axes should lie
     */
    void set_structure(const std::shared_ptr<Structure> structure, const glm::mat3x3 cartesian_axes);

    /**
     * @brief Set the operation that should be rendered
     *
     * @param operation
     */
    void set_operation(const Operation operation);

    /**
     * @brief Unset the operation
     *
     */
    void unset_operation();

    /**
     * @brief Reset camera
     */
    void reset_camera();

    /**
     * @brief Highlight an atom by index
     *
     * @param index
     */
    void highlight_atom(unsigned int index);

    /**
     * @brief Unhighlight an atom by index
     *
     * @param index
     */
    void unhighlight_atom(unsigned int index);

    /**
     * @brief Unhighlight all atoms
     */
    void unhighlight_atoms();

    /**
     * @brief Set a custom label
     *
     * @param index
     * @param label
     */
    void set_custom_label(unsigned int index, const std::string& label);

    /**
     * @brief Clear all custom labels
     */
    void clear_custom_labels();

    /**
     * @brief Start animating an operation
     *
     * @param operation
     */
    void start_animation(const Operation operation);

    /**
     * @brief Get the structure rotation matrix
     *
     * @return const glm::mat4x4
     */
    const glm::mat4x4 get_structure_rotation() const;

    /**
     * @brief Get the structure span
     *
     * @return const float
     */
    const float get_structure_span() const;

    /**
     * @brief Get the model instances to draw the structure
     *
     * @return std::vector<ModelInstance>
     */
    std::vector<ModelInstance> get_structure_model_instances();

    /**
     * @brief Get the model instances to draw the silhouette
     *
     * @return std::vector<ModelInstance>
     */
    std::vector<ModelInstance> get_silhouette_model_instances();

    /**
     * @brief Get the model instances to draw the operation
     *
     * @return std::vector<ModelInstance>
     */
    std::vector<ModelInstance> get_operation_model_instances();

    /**
     * @brief Get the model instances to draw labels
     *
     * @return std::vector<ModelInstance>
     */
    std::vector<ModelInstance> get_label_model_instances();

    /**
     * @brief Get whether the structure is animating
     *
     * @return true
     * @return false
     */
    const bool get_animating() const;

    /**
     * @brief Set the arcball rotation matrix
     *
     * @param angle rotation angle
     * @param vector rotation vector
     */
    void set_arcball_rotation(float angle, glm::vec3 vector);

    /**
     * @brief Apply the arcball rotation matrix to the camera rotation matrix
     */
    void apply_arcball_rotation();

    /**
     * @brief Get the transformation matrix after applying the base camera
     * rotation transformations
     *
     * @return glm::mat4x4
     */
    glm::mat4x4 base_camera_matrix();

    /**
     * @brief Get the transformation matrix after applying the base structure
     * rotation transformations
     *
     * @return glm::mat4x4
     */
    glm::mat4x4 base_matrix();

private:
    /**
     * @brief Calculate and set the structure span
     */
    void calculate_structure_span();

    /**
     * @brief Calculate and set pairs of elements between which bonds are
     * (likely) formed
     */
    void calculate_bond_pairs();

    /**
     * @brief Create and set the list of atom indices after animation
     */
    void create_animated_indices();

    /**
     * @brief Create and set the list of default atom labels
     */
    void create_default_labels();

    /**
     * @brief Get whether custom labels should be visible
     *
     * @return true
     * @return false
     */
    bool get_custom_labels_visible();

    /**
     * @brief Compute the rotation matrix to rotate an object aligned along the
     * z axis towards the given axis
     *
     * @param axis
     * @return glm::mat4x4 rotation matrix
     */
    glm::mat4x4 rotation_matrix_from_axis_vector(const glm::vec3 axis);

    /**
     * @brief Apply a symmetry operation to the list of atom indices
     *
     * @param operation
     */
    void apply_operation_to_animated_indices(Operation operation);

public slots:
    /**
     * @brief Process any running animations
     */
    void process_animations();

    /**
     * @brief Set the visibility of the default labels
     *
     * @param visible
     */
    void set_default_labels_visible(bool visible);

signals:
    /**
     * @brief Update the GL widget
     */
    void update();

    /**
     * @brief Signal to send when the current animation has finished
     */
    void animation_finished();
};

#endif  // STRUCTURE_RENDERER_H
