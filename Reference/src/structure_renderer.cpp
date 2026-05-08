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

#include "structure_renderer.h"

/**
 * @brief Default constructor
 *
 * @param freetype_font
 */
StructureRenderer::StructureRenderer(const std::shared_ptr<FreeTypeFont> freetype_font) {
    this->freetype_font = freetype_font;
}

/**
 * @brief Set the structure
 *
 * @param structure structure to render from
 * @param cartesian_axes structure rotation to correctly align to Cartesian axes
 */
void StructureRenderer::set_structure(const std::shared_ptr<Structure> structure, const glm::mat3x3 cartesian_axes) {
    this->structure_set = true;
    this->operation_set = false;

    this->structure = structure;
    this->structure_rotation = glm::mat4x4(glm::inverse(cartesian_axes));
    this->animation_matrix = glm::mat3x3(1.0f);

    this->calculate_structure_span();
    this->calculate_bond_pairs();
    this->create_animated_indices();
    this->create_default_labels();

    this->unhighlight_atoms();
    this->clear_custom_labels();
}

/**
 * @brief Set the operation that should be rendered
 *
 * @param operation
 */
void StructureRenderer::set_operation(const Operation operation) {
    this->operation_set = true;
    this->operation = operation;
}

/**
 * @brief Unset the operation
 *
 */
void StructureRenderer::unset_operation() {
    this->operation_set = false;
}

/**
 * @brief Reset camera rotation
 */
void StructureRenderer::reset_camera() {
    this->camera_rotation = glm::mat4x4(1.0f);
    this->camera_rotation = glm::rotate(this->camera_rotation, 60.0f * (float) M_PI / 180.0f, glm::vec3(1.0f, 0.0f, 0.0f));
    this->camera_rotation = glm::rotate(this->camera_rotation, 20.0f * (float) M_PI / 180.0f, glm::vec3(0.0f, 0.0f, 1.0f));

    this->arcball_rotation = glm::mat4x4(1.0f);
}

/**
 * @brief Highlight an atom by index
 *
 * @param index
 */
void StructureRenderer::highlight_atom(unsigned int index) {
    if (!this->structure_set) throw std::runtime_error("No structure set.");

    if (index < this->structure->get_num_atoms()) {
        this->highlighted_atoms.insert(index);
    } else {
        throw std::runtime_error("Requested invalid atom index.");
    }
}

/**
 * @brief Unhighlight an atom by index
 *
 * @param index
 */
void StructureRenderer::unhighlight_atom(unsigned int index) {
    if (!this->structure_set) throw std::runtime_error("No structure set.");

    if (index < this->structure->get_num_atoms()) {
        this->highlighted_atoms.erase(index);
    } else {
        throw std::runtime_error("Requested invalid atom index.");
    }
}

/**
 * @brief Unhighlight all atoms
 */
void StructureRenderer::unhighlight_atoms() {
    this->highlighted_atoms.clear();
}

/**
 * @brief Set a custom atom label
 *
 * @param index
 * @param label
 */
void StructureRenderer::set_custom_label(unsigned int index, const std::string& label) {
    if (!this->structure_set) throw std::runtime_error("No structure set.");

    if (index < this->structure->get_num_atoms()) {
        this->custom_labels[index] = label;
    } else {
        throw std::runtime_error("Requested invalid atom index.");
    }
}

/**
 * @brief Clear all custom atom labels
 */
void StructureRenderer::clear_custom_labels() {
    this->custom_labels.clear();
}

/**
 * @brief Start animating an operation
 *
 * @param operation
 */
void StructureRenderer::start_animation(const Operation operation) {
    this->operation = operation;
    this->animating = true;
    this->animation_start_time = std::chrono::high_resolution_clock::now();
}

/**
 * @brief Get the structure rotation matrix
 *
 * @return const glm::mat4x4
 */
const glm::mat4x4 StructureRenderer::get_structure_rotation() const {
    return this->structure_rotation;
}

/**
 * @brief Get the structure span
 *
 * @return const float
 */
const float StructureRenderer::get_structure_span() const {
    return this->structure_span;
}

/**
 * @brief Get the model instances to draw the structure
 *
 * @return std::vector<ModelInstance>
 */
std::vector<ModelInstance> StructureRenderer::get_structure_model_instances() {
    std::vector<ModelInstance> model_instances;
    if (!this->structure_set) return model_instances;

    for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
        Element el = PeriodicTable::get_element(this->structure->get_atomic_number(i));
        glm::vec3 coordinates = this->animation_matrix * this->structure->get_coordinates(i);

        glm::mat4x4 transform = glm::scale(glm::translate(this->base_matrix(), coordinates), glm::vec3(el.radius));

        model_instances.push_back({"sphere", transform, glm::vec4(el.colour, 1.0f), -1});
    }

    for (std::pair<unsigned int, unsigned int> bond_pair : this->bond_pairs) {
        Element el_a = PeriodicTable::get_element(this->structure->get_atomic_number(bond_pair.first));
        Element el_b = PeriodicTable::get_element(this->structure->get_atomic_number(bond_pair.second));

        glm::vec3 coords_a = this->animation_matrix * this->structure->get_coordinates(bond_pair.first);
        glm::vec3 coords_b = this->animation_matrix * this->structure->get_coordinates(bond_pair.second);

        glm::vec3 v = coords_b - coords_a;
        float vl = glm::length(v);

        // place the 'seam' between cylinders in the middle of the atom surfaces
        float scale_factor = 0.5 + (el_a.radius - el_b.radius) / vl / 2;

        glm::vec3 trans_a = coords_a;
        glm::vec3 trans_b = trans_a + scale_factor * v;

        glm::vec3 scale_a = {0.05f, 0.05f, scale_factor * vl};
        glm::vec3 scale_b = {0.05f, 0.05f, (1 - scale_factor) * vl};

        glm::mat4x4 rotation = this->rotation_matrix_from_axis_vector(v);

        glm::mat4x4 transform_a = glm::scale(glm::translate(this->base_matrix(), trans_a) * rotation, scale_a);
        glm::mat4x4 transform_b = glm::scale(glm::translate(this->base_matrix(), trans_b) * rotation, scale_b);

        model_instances.push_back({"cylinder", transform_a, glm::vec4(el_a.colour, 1.0f), -1});
        model_instances.push_back({"cylinder", transform_b, glm::vec4(el_b.colour, 1.0f), -1});
    }

    return model_instances;
}

/**
 * @brief Get the model instances to draw the silhouette
 *
 * @return std::vector<ModelInstance>
 */
std::vector<ModelInstance> StructureRenderer::get_silhouette_model_instances() {
    std::vector<ModelInstance> model_instances;
    if (!this->structure_set) return model_instances;

    for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
        Element el = PeriodicTable::get_element(this->structure->get_atomic_number(i));
        glm::vec3 coordinates = this->animation_matrix * this->structure->get_coordinates(i);

        glm::vec4 silhouette_colour;
        unsigned int ai = this->animated_indices[i];
        if (this->highlighted_atoms.find(ai) != this->highlighted_atoms.end()) {
            // unique but not black
            float fi = (float) (i + 1) / this->structure->get_num_atoms();
            silhouette_colour = glm::vec4(1.0f, fi, 0.0f, 1.0f);
        } else {
            silhouette_colour = glm::vec4(0.0f, 0.0f, 0.0f, 1.0f);
        }

        glm::mat4x4 transform = glm::scale(glm::translate(this->base_matrix(), coordinates), glm::vec3(el.radius));

        model_instances.push_back({"sphere", transform, silhouette_colour, -1});
    }

    for (std::pair<unsigned int, unsigned int> bond_pair : this->bond_pairs) {
        Element el_a = PeriodicTable::get_element(this->structure->get_atomic_number(bond_pair.first));
        Element el_b = PeriodicTable::get_element(this->structure->get_atomic_number(bond_pair.second));

        glm::vec3 coords_a = this->animation_matrix * this->structure->get_coordinates(bond_pair.first);
        glm::vec3 coords_b = this->animation_matrix * this->structure->get_coordinates(bond_pair.second);

        glm::vec3 v = coords_b - coords_a;
        float vl = glm::length(v);

        glm::vec3 trans = coords_a;
        glm::vec3 scale = {0.05f, 0.05f, vl};
        glm::mat4 rotation = this->rotation_matrix_from_axis_vector(v);

        glm::mat4x4 transform = glm::scale(glm::translate(this->base_matrix(), trans) * rotation, scale);

        model_instances.push_back({"cylinder", transform, glm::vec4(0.0f, 0.0f, 0.0f, 1.0f), -1});
    }

    return model_instances;
}

/**
 * @brief Get the model instances to draw the operation
 *
 * @return std::vector<ModelInstance>
 */
std::vector<ModelInstance> StructureRenderer::get_operation_model_instances() {
    std::vector<ModelInstance> model_instances;
    if (!this->structure_set || !this->operation_set) return model_instances;

    OperationLabel::Element element = this->operation.get_label().get_element();
    glm::vec3 colour = this->operation.get_label().get_colour();
    glm::mat4x4 rotation = this->rotation_matrix_from_axis_vector(this->operation.get_axis());

    if (element == OperationLabel::Element::Inversion) {
        glm::mat4x4 transform = glm::scale(this->base_matrix(), glm::vec3(0.25f));
        model_instances.push_back({"sphere", transform, glm::vec4(colour, 1.0f), -1});
    }

    if (element == OperationLabel::Element::ProperRotation ||
        element == OperationLabel::Element::ImproperRotation) {
        glm::vec3 trans = -(this->structure_span + 0.2f) * this->operation.get_axis();
        glm::vec3 scale = glm::vec3(0.04f, 0.04f, 2 * this->structure_span + 0.4f);
        glm::mat4x4 transform = glm::scale(glm::translate(this->base_matrix(), trans) * rotation, scale);
        model_instances.push_back({"cylinder_capped", transform, glm::vec4(colour, 1.0f), -1});
    }

    if (element == OperationLabel::Element::Reflection ||
        element == OperationLabel::Element::ImproperRotation) {
        glm::vec3 scale = glm::vec3(this->structure_span + 0.2f);
        glm::mat4x4 transform = glm::scale(this->base_matrix() * rotation, scale);
        model_instances.push_back({"circle", transform, glm::vec4(colour, 0.5f), -1});
    }

    return model_instances;
}

/**
 * @brief Get the model instances to draw labels
 *
 * @return std::vector<ModelInstance>
 */
std::vector<ModelInstance> StructureRenderer::get_label_model_instances() {
    std::vector<ModelInstance> model_instances;
    if (!this->structure_set || (!this->default_labels_visible && !this->get_custom_labels_visible()))
        return model_instances;

    const float font_scale = 0.004f;

    for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
        Element el = PeriodicTable::get_element(this->structure->get_atomic_number(i));
        glm::vec3 coordinates = this->animation_matrix * this->structure->get_coordinates(i);

        unsigned int ai = this->animated_indices[i];

        std::string label;
        if (this->get_custom_labels_visible()) {
            auto it = this->custom_labels.find(ai);
            if (it == this->custom_labels.end()) continue;
            label = it->second;
        } else if (this->default_labels_visible) {  // custom labels override default labels
            label = this->default_labels[ai];
        } else {
            continue;
        }
        glm::ivec2 label_size = this->freetype_font->get_string_size(label);

        float x_off = -label_size.x / 2;
        for (unsigned int ci = 0; ci < label.size(); ++ci) {
            Character ch = this->freetype_font->get_character(label[ci]);
            glm::vec3 scale = glm::vec3(font_scale * el.radius * glm::vec2(ch.size), 1.0f);

            glm::vec2 trans = font_scale * el.radius * glm::vec2(
                x_off + ch.bearing.x + ch.size.x,
                ch.size.y - 2 * (ch.size.y - ch.bearing.y) - label_size.y
            );

            glm::mat4x4 transform = glm::translate(this->base_matrix(), coordinates)
                * glm::transpose(this->base_matrix())
                * this->rotation_matrix_from_axis_vector(glm::vec3(0.0f, -1.0f, 0.0f));
            transform = glm::scale(glm::translate(transform, glm::vec3(trans, el.radius)), scale);

            model_instances.push_back({"quad_3d", transform, glm::vec4(1.0f), ch.texture_id});

            x_off += 2 * ch.advance / 64;
        }
    }

    return model_instances;
}

/**
 * @brief Get whether the structure is animating
 *
 * @return true
 * @return false
 */
const bool StructureRenderer::get_animating() const {
    return this->animating;
}

/**
 * @brief Set the arcball rotation matrix
 *
 * @param angle rotation angle
 * @param vector rotation vector
 */
void StructureRenderer::set_arcball_rotation(float angle, glm::vec3 vector) {
    this->arcball_rotation = glm::rotate(glm::mat4x4(1.0f), angle, vector);
}

/**
 * @brief Apply the arcball rotation to the camera rotation
 */
void StructureRenderer::apply_arcball_rotation() {
    this->camera_rotation = this->arcball_rotation * this->camera_rotation;
    this->arcball_rotation = glm::mat4x4(1.0f);
}

/**
 * @brief Get the transformation matrix after applying the base camera
 * rotation transformations
 *
 * @return glm::mat4x4
 */
glm::mat4x4 StructureRenderer::base_camera_matrix() {
    return this->arcball_rotation * this->camera_rotation;
}

/**
 * @brief Get the transformation matrix after applying the base structure
 * rotation transformations
 *
 * @return glm::mat4x4
 */
glm::mat4x4 StructureRenderer::base_matrix() {
    return this->arcball_rotation * this->camera_rotation * this->structure_rotation;
}

/**
 * @brief Calculate and set the structure span
 */
void StructureRenderer::calculate_structure_span() {
    this->structure_span = 0;

    for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
        Element el = PeriodicTable::get_element(this->structure->get_atomic_number(i));
        float span = glm::length(this->structure->get_coordinates(i)) + el.radius;
        if (span > this->structure_span) this->structure_span = span;
    }
}

/**
 * @brief Calculate and set pairs of elements between which bonds are
 * (likely) formed
 */
void StructureRenderer::calculate_bond_pairs() {
    this->bond_pairs.clear();

    for (unsigned int i = 0; i < this->structure->get_num_atoms() - 1; ++i) {
        for (unsigned int j = i + 1; j < this->structure->get_num_atoms(); ++j) {
            float dist2 = glm::length2(this->structure->get_coordinates(i) - this->structure->get_coordinates(j));
            float thres = 20 * PeriodicTable::get_element(this->structure->get_atomic_number(i)).radius *
                PeriodicTable::get_element(this->structure->get_atomic_number(j)).radius;
            if (dist2 < thres) this->bond_pairs.emplace_back(i, j);
        }
    }
}

/**
 * @brief Create and set the list of atom indices after animation
 */
void StructureRenderer::create_animated_indices() {
    this->animated_indices = std::vector<unsigned int>(this->structure->get_num_atoms());
    // start without any animation
    std::iota(this->animated_indices.begin(), this->animated_indices.end(), 0);
}

/**
 * @brief Create and set the list of default atom labels
 */
void StructureRenderer::create_default_labels() {
    this->default_labels.clear();
    std::unordered_map<unsigned int, unsigned int> element_counter;

    for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
        unsigned int atomic_number = this->structure->get_atomic_number(i);
        unsigned int count = ++element_counter[atomic_number];

        Element el = PeriodicTable::get_element(atomic_number);
        this->default_labels.push_back(el.symbol + std::to_string(count));
    }
}

/**
 * @brief Get whether custom labels should be visible
 *
 * @return true
 * @return false
 */
bool StructureRenderer::get_custom_labels_visible() {
    return this->custom_labels.size() > 0;
}

/**
 * @brief Compute the rotation matrix to rotate an object aligned along the
 * z axis towards the given axis
 *
 * @param axis
 * @return glm::mat4x4 rotation matrix
 */
glm::mat4x4 StructureRenderer::rotation_matrix_from_axis_vector(const glm::vec3 axis) {
    glm::vec3 axis_n = glm::normalize(axis);
    glm::mat4x4 rotation(1.0f);

    if (std::fabs(axis_n.z) > .9999f) {
        if (axis_n.z < -.5f) {
            rotation = glm::rotate(glm::mat4x4(1.0f), -(float) M_PI, glm::vec3(0.0f, 1.0f, 0.0f));
        }
    } else {
        float angle = std::acos(axis_n.z);
        glm::vec3 axis_angle = glm::normalize(glm::cross(glm::vec3(0.0f, 0.0f, 1.0f), axis));
        rotation = glm::rotate(glm::mat4x4(1.0f), angle, axis_angle);
    }

    return rotation;
}

/**
 * @brief Apply a symmetry operation to the list of atom indices
 *
 * @param operation
 */
void StructureRenderer::apply_operation_to_animated_indices(Operation operation) {
    std::vector<unsigned int> animated_indices_copy = this->animated_indices;  // temporary copy

    for (unsigned int i = 0; i < animated_indices_copy.size(); ++i) {
        unsigned int original_index = animated_indices_copy[i];
        this->animated_indices[operation.get_result_index(i)] = original_index;
    }
}

/**
 * @brief Process any running animations
 */
void StructureRenderer::process_animations() {
    if (!this->animating) return;

    auto now = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> runtime = now - this->animation_start_time;
    double seconds = runtime.count();
    double f = seconds / 1.0;  // TODO make animation duration variable

    glm::mat3x3 animation_matrix;

    if (f > 1) {
        f = 1;
        this->animating = false;
        this->animation_matrix = glm::mat3x3(1.0f);  // reset to identity matrix
        this->apply_operation_to_animated_indices(this->operation);
        emit this->animation_finished();
    } else {
        this->animation_matrix = this->operation.calculate_fractional_matrix(f);
    }

    emit this->update();
}

/**
 * @brief Set the visibility of the default labels
 *
 * @param visible
 */
void StructureRenderer::set_default_labels_visible(bool visible) {
    this->default_labels_visible = visible;
    emit this->update();
}
