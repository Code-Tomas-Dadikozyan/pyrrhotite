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

#ifndef SYMMETRY_SYMMETRY_H
#define SYMMETRY_SYMMETRY_H

#include <cmath>
#include <limits>
#include <math.h>
#include <memory>
#include <stdexcept>
#include <vector>
#include <Eigen/Dense>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_access.hpp>
#include "../structure.h"
#include "rotor_class.h"
#include "operations/operation.h"
#include "operations/operation_label.h"
#include "operations/operation_manager.h"
#include "point_groups/point_group.h"
#include "point_groups/point_group_label.h"
#include "point_groups/point_groups.h"

class Symmetry {
private:
    std::shared_ptr<Structure> structure;
    std::shared_ptr<OperationManager> operation_manager;

    glm::vec3 principal_moments;
    glm::mat3x3 principal_axes;

    glm::vec3 x_axis{NAN};
    glm::vec3 y_axis{NAN};
    glm::vec3 z_axis{NAN};

    RotorClass rotor_class;

    PointGroup point_group;

public:
    /**
     * @brief Default constructor
     */
    Symmetry();

    /**
     * @brief Construct a new Symmetry object
     *
     * @param structure
     */
    Symmetry(std::shared_ptr<Structure> structure);

    /**
     * @brief Get the structure object
     *
     * @return const std::shared_ptr<Structure>
     */
    const std::shared_ptr<Structure> get_structure() const;

    /**
     * @brief Get the principal moments of the structure
     *
     * @return const glm::vec3&
     */
    const glm::vec3& get_principal_moments() const;

    /**
     * @brief Get the principal axes of the structure
     *
     * @return const glm::mat3x3&
     */
    const glm::mat3x3& get_principal_axes() const;

    /**
     * @brief Get the x axis of the structure
     *
     * @return const glm::vec3&
     */
    const glm::vec3& get_x_axis() const;

    /**
     * @brief Get the y axis of the structure
     *
     * @return const glm::vec3&
     */
    const glm::vec3& get_y_axis() const;

    /**
     * @brief Get the z axis of the structure
     *
     * @return const glm::vec3&
     */
    const glm::vec3& get_z_axis() const;

    /**
     * @brief Get the cartesian axes of the structure
     *
     * @return const glm::mat3x3
     */
    const glm::mat3x3 get_cartesian_axes() const;

    /**
     * @brief Get the rotor class of the structure
     *
     * @return const RotorClass
     */
    const RotorClass get_rotor_class() const;

    /**
     * @brief Get the operation manager object
     *
     * @return const std::shared_ptr<OperationManager>&
     */
    const std::shared_ptr<OperationManager>& get_operation_manager() const;

    /**
     * @brief Get the point group of the structure
     *
     * @return const PointGroup&
     */
    const PointGroup& get_point_group() const;

private:
    /**
     * @brief Calculate the inertial tensor and use this to determine principal
     * axes and their principal moments.
     */
    void determine_principal_axes();

    /**
     * @brief Determine the rotor class of the structure (given by the
     * degeneracy of the inertial moments).
     */
    void determine_rotor_class();

    /**
     * @brief Find all symmetry operations of the structure.
     */
    void find_symmetry_operations();

    /**
     * @brief Find an inversion centre in the structure.
     */
    void find_inversion_centre();

    /**
     * @brief Find proper rotational axes in the structure.
     */
    void find_proper_rotational_axes();

    /**
     * @brief Find proper rotational axes along the principal axes of the
     * structure.
     */
    void find_proper_rotational_axes_along_principal_axes();

    /**
     * @brief Find proper rotational axes through the centre of mass and an
     * atom of the structure.
     */
    void find_proper_rotational_axes_through_atoms();

    /**
     * @brief Find proper rotational axes through the centre of mass and the
     * midpoints between pairs of atoms of the same element.
     */
    void find_proper_rotational_axes_between_atoms();

    /**
     * @brief Find proper rotational axes through polygonal faces for
     * structures classified as spherical top (cubic).
     */
    void find_proper_rotational_axes_polygonal_faces();

    /**
     * @brief Find proper rotational axes through polygonal faces for
     * structures with tetrahedral symmetry (T point group, 3 C2 rotations) and
     * octahedral symmetry (O point group, 9 C2 rotations).
     */
    void find_proper_rotational_axes_polygonal_faces_T_O();

    /**
     * @brief Find proper rotational axes through polygonal faces for
     * structures with icosahedral symmetry (I point group, 15 C2 rotations).
     *
     * @param C2s C2 rotations present in the structure
     */
    void find_proper_rotational_axes_polygonal_faces_I(std::vector<Operation> C2s);

    /**
     * @brief Find improper rotational axes in the structure.
     */
    void find_improper_rotational_axes();

    /**
     * @brief Find reflection planes in the structure.
     */
    void find_reflection_planes();

    /**
     * @brief Find reflection planes which are normal to the principal axes of
     * the structure.
     */
    void find_reflection_planes_normal_to_principal_axes();

    /**
     * @brief Find reflection planes which are normal to proper rotational
     * axes.
     *
     * @param only_C2s whether to only search normal to C2 rotational axes (in
     * case of octahedral and icosahedral symmetry)
     */
    void find_reflection_planes_normal_to_proper_rotational_axes(bool only_C2s);

    /**
     * @brief Find reflection planes which pass through midpoints between pairs
     * of atoms of the same element.
     */
    void find_reflection_planes_in_midpoints();

    /**
     * @brief Find the point group with the highest match to the found symmetry
     * operations.
     */
    void find_point_group();

    /**
     * @brief Find the Cartesian axes of the structure, according to molecular
     * symmetry conventions.
     */
    void find_cartesian_axes();

    /**
     * @brief Assign two of the principal axes of the structure (from the
     * inertial tensor) to the Cartesian x and z axes.
     */
    void assign_principal_axes_to_cartesian_xz_axes();

    /**
     * @brief Find the z axis (principal axis) of the structure.
     */
    void find_z_axis();

    /**
     * @brief Find the best-fitting plane through all atoms using a singular
     * value decomposition.
     *
     * @return glm::vec3 best-fitting plane
     */
    glm::vec3 find_plane_normal();

    /**
     * @brief Determine whether the structure is planar by comparing the
     * positions of the atoms to the best-fitting plane.
     *
     * @param plane_normal best-fitting plane
     * @return true if structure is planar
     * @return false if structure is not planar
     */
    bool structure_is_planar(glm::vec3& plane_normal);

    /**
     * @brief Find the x axis of the structure under the assumption that the
     * structure is planar.
     *
     * @param plane_normal best-fitting plane
     */
    void find_x_axis_planar(glm::vec3& plane_normal);

    /**
     * @brief Find the x axis of the structure under the assumption that the
     * structure is not planar.
     */
    void find_x_axis_not_planar();

    /**
     * @brief Pick an arbitrary x axis for the structure if it is linear.
     */
    void pick_arbitrary_x_axis();

    /**
     * @brief Orthonormalise the x axis with respect to the z axis of the
     * structure using the Gram-Schmidt procedure.
     */
    void orthonormalise_xz_axes();

    /**
     * @brief Find the y axis of the structure using the x and z axes.
     */
    void find_y_axis();

    /**
     * @brief Label the symmetry operations based on the point group and their
     * orientations with respect to the Cartesian axes.
     */
    void label_symmetry_operations();

    /**
     * @brief Label the proper rotational axes.
     */
    void label_proper_rotational_axes();

    /**
     * @brief Label the proper rotational axes for dihedral point groups.
     */
    void label_proper_rotational_axes_dihedral();

    /**
     * @brief Label the proper rotational axes for octahedral point groups.
     */
    void label_proper_rotational_axes_octahedral();

    /**
     * @brief Label the reflection planes.
     */
    void label_reflection_planes();

    /**
     * @brief Label the reflection planes for cyclic and dihedral point groups.
     */
    void label_reflection_planes_cyclic_dihedral();

    /**
     * @brief Label the reflection planes for tetrahedral point groups.
     */
    void label_reflection_planes_tetrahedral();

    /**
     * @brief Label the reflection planes for octahedral point groups.
     */
    void label_reflection_planes_octahedral();

    /**
     * @brief Check whether an axis can be a symmetry axis based on the
     * inertial tensor.
     *
     * A symmetry operation must leave a molecule unchanged, which sets
     * restrictions on whether an axis or plane can be a symmetry axis or plane
     * based on the principal axes. Checking this early leads to increased
     * efficiency.
     *
     * @param axis the axis to check
     * @return true if axis can be a symmetry axis
     * @return false if axis cannot be a symmetry axis
     */
    bool axis_inertially_allowed(glm::vec3& axis);
};

#endif  // SYMMETRY_SYMMETRY_H
