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

#include "symmetry.h"

/**
 * @brief Default constructor
 */
Symmetry::Symmetry() {}

/**
 * @brief Construct a new Symmetry object
 *
 * @param structure
 */
Symmetry::Symmetry(std::shared_ptr<Structure> structure) {
    this->structure = structure;
    this->operation_manager = std::make_shared<OperationManager>(structure);

    this->determine_principal_axes();
    this->determine_rotor_class();
    this->find_symmetry_operations();
    this->find_point_group();
    this->find_cartesian_axes();
    this->label_symmetry_operations();

    this->operation_manager->generate_point_group_operations(this->point_group);
}

/**
 * @brief Get the structure object
 *
 * @return const std::shared_ptr<Structure>
 */
const std::shared_ptr<Structure> Symmetry::get_structure() const {
    return this->structure;
}

/**
 * @brief Calculate the inertial tensor and use this to determine principal
 * axes and their principal moments.
 */
void Symmetry::determine_principal_axes() {
    // calculate inertial tensor
    double Ixx = 0, Iyy = 0, Izz = 0, Ixy = 0, Ixz = 0, Iyz = 0;

    for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
        float mass = PeriodicTable::get_element(this->structure->get_atomic_number(i)).mass;
        glm::vec3 r = this->structure->get_coordinates(i);

        Ixx += mass * (r.y * r.y + r.z * r.z);
        Iyy += mass * (r.x * r.x + r.z * r.z);
        Izz += mass * (r.x * r.x + r.y * r.y);

        Ixy -= mass * r.x * r.y;
        Ixz -= mass * r.x * r.z;
        Iyz -= mass * r.y * r.z;
    }

    // symmetrix matrix with only real entries <=> self-adjoint matrix
    Eigen::Matrix3d I;
    I << Ixx, Ixy, Ixz,
         Ixy, Iyy, Iyz,
         Ixz, Iyz, Izz;

    Eigen::SelfAdjointEigenSolver<Eigen::Matrix3d> solver(I);

    if (solver.info() != Eigen::ComputationInfo::Success) {
        throw std::runtime_error("Diagonalisation of inertial tensor did not converge.");
    }

    auto& principal_moments = solver.eigenvalues();
    auto& principal_axes = solver.eigenvectors();

    // convert Eigen objects to GLM objects
    for (unsigned int i = 0; i < 3; ++i) {
        for (unsigned int j = 0; j < 3; ++j) {
            this->principal_axes[i][j] = principal_axes(j, i);
        }

        this->principal_moments[i] = principal_moments(i);
    }
}

/**
 * @brief Determine the rotor class of the structure (given by the
 * degeneracy of the inertial moments).
 */
void Symmetry::determine_rotor_class() {
    // TODO move tolerance to a variable/constant

    // we use the fact that the eigenvalues are sorted in increasing order
    // (from Eigen docs)
    if ((this->principal_moments[2] - this->principal_moments[0]) / this->principal_moments[2] < .02) {
        // all principal moments are (approximately) degenerate
        this->rotor_class = RotorClass::SphericalTop;
    } else if ((this->principal_moments[1] - this->principal_moments[0]) / this->principal_moments[1] < .02) {
        // the two lower principal moments are (approximately) degenerate
        this->rotor_class = RotorClass::OblateSymmetricTop;
    } else if ((this->principal_moments[2] - this->principal_moments[1]) / this->principal_moments[2] < .02) {
        // the two higher principal moments are (approximately) degenerate
        if (this->principal_moments[0] < .02) {
            // the lowest principal moment is (approximately) zero
            this->rotor_class = RotorClass::Linear;
        } else {
            this->rotor_class = RotorClass::ProlateSymmetricTop;
        }
    } else {
        // all principal moments are unique
        this->rotor_class = RotorClass::AsymmetricTop;
    }
}

/**
 * @brief Find all symmetry operations of the structure.
 */
void Symmetry::find_symmetry_operations() {
    this->find_inversion_centre();
    this->find_proper_rotational_axes();
    this->find_improper_rotational_axes();
    this->find_reflection_planes();
}

/**
 * @brief Find an inversion centre in the structure.
 */
void Symmetry::find_inversion_centre() {
    Operation inversion(OperationLabel::Element::Inversion);
    this->operation_manager->add_operation(inversion);
}

/**
 * @brief Find proper rotational axes in the structure.
 */
void Symmetry::find_proper_rotational_axes() {
    if (this->get_rotor_class() == RotorClass::Linear) {
        // only C∞ for linear structures
        glm::vec3 axis = glm::column(this->get_principal_axes(), 0);

        Operation rotation(OperationLabel::Element::ProperRotation, Operation::DEGREE_INF, axis);
        this->operation_manager->add_operation(rotation);
    } else {
        this->find_proper_rotational_axes_along_principal_axes();
        this->find_proper_rotational_axes_through_atoms();
        this->find_proper_rotational_axes_between_atoms();

        if (this->get_rotor_class() == RotorClass::SphericalTop) {
            this->find_proper_rotational_axes_polygonal_faces();
        }
    }
}

/**
 * @brief Find proper rotational axes along the principal axes of the
 * structure.
 */
void Symmetry::find_proper_rotational_axes_along_principal_axes() {
    for (unsigned int i = 0; i < 3; ++i) {
        glm::vec3 axis = glm::column(this->get_principal_axes(), i);

        // TODO move maximum degree to a constant
        for (unsigned int degree = 2; degree <= 8; ++degree) {
            Operation rotation(OperationLabel::Element::ProperRotation, degree, axis);
            this->operation_manager->add_operation(rotation);
        }
    }
}

/**
 * @brief Find proper rotational axes through the centre of mass and an
 * atom of the structure.
 */
void Symmetry::find_proper_rotational_axes_through_atoms() {
    for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
        glm::vec3 axis = this->structure->get_coordinates(i);

        if (glm::length2(axis) == 0) continue;
        if (!this->axis_inertially_allowed(axis)) continue;

        // TODO move maximum degree to a constant
        for (unsigned int degree = 2; degree <= 8; ++degree) {
            Operation rotation(OperationLabel::Element::ProperRotation, degree, axis);
            this->operation_manager->add_operation(rotation);
        }
    }
}

/**
 * @brief Find proper rotational axes through the centre of mass and the
 * midpoints between pairs of atoms of the same element.
 */
void Symmetry::find_proper_rotational_axes_between_atoms() {
    for (unsigned int i = 0; i < this->structure->get_num_atoms() - 1; ++i) {
        for (unsigned int j = i + 1; j < this->structure->get_num_atoms(); ++j) {
            if (this->structure->get_atomic_number(i) != this->structure->get_atomic_number(j)) continue;
            if (this->get_rotor_class() == RotorClass::SphericalTop) {
                // skip if distance between atoms of pair is too large
                const float d2 = glm::distance2(this->structure->get_coordinates(i),
                                                this->structure->get_coordinates(j));
                if (d2 > 16) continue;
            }

            // calculate midpoint between atoms i and j
            glm::vec3 axis = .5f * (this->structure->get_coordinates(i) + this->structure->get_coordinates(j));

            if (glm::length2(axis) == 0) continue;
            if (!this->axis_inertially_allowed(axis)) continue;

            // we know that this axis lies along a midpoint of atoms,
            // therefore it must have an even degree
            // TODO move maximum degree to a constant
            for (unsigned int degree = 2; degree <= 8; degree += 2) {
                Operation rotation(OperationLabel::Element::ProperRotation, degree, axis);
                bool operation_exists = this->operation_manager->add_operation(rotation);
                // if C2 doesn't exist, further Cn with even n won't exist either
                if (degree == 2 && !operation_exists) break;
            }
        }
    }
}

/**
 * @brief Find proper rotational axes through polygonal faces for
 * structures classified as spherical top (cubic).
 */
void Symmetry::find_proper_rotational_axes_polygonal_faces() {
    // the number of C2 rotations determines how we find the remaining axes
    std::vector<Operation> C2s;

    for (Operation& operation : this->operation_manager->get_operations()) {
        if (operation.get_label().get_element() == OperationLabel::Element::ProperRotation &&
            operation.get_degree() == 2) {
            C2s.push_back(operation);
        }
    }

    switch (C2s.size()) {
        case 3:
        case 9:
            this->find_proper_rotational_axes_polygonal_faces_T_O();
            break;
        case 15:
            this->find_proper_rotational_axes_polygonal_faces_I(C2s);
            break;
    }
}

/**
 * @brief Find proper rotational axes through polygonal faces for
 * structures with tetrahedral symmetry (T point group, 3 C2 rotations) and
 * octahedral symmetry (O point group, 9 C2 rotations).
 */
void Symmetry::find_proper_rotational_axes_polygonal_faces_T_O() {
    // the remaining C3 rotations are formed by combining the three principal axes
    // we only need to enumerate half of the combinations; the other half are
    // the same axes but in opposite directions
    for (int i = -1; i < 2; i += 2) {  // {-1, 1}
        for (int j = -1; j < 2; j += 2) {  // {-1, 1}
            glm::vec3 axis = glm::column(this->get_principal_axes(), 0) * (float) i +
                             glm::column(this->get_principal_axes(), 1) * (float) j +
                             glm::column(this->get_principal_axes(), 2);

            Operation rotation(OperationLabel::Element::ProperRotation, 3, axis);
            this->operation_manager->add_operation(rotation);
        }
    }
}

/**
 * @brief Find proper rotational axes through polygonal faces for
 * structures with icosahedral symmetry (I point group, 15 C2 rotations).
 *
 * @param C2s C2 rotations present in the structure
 */
void Symmetry::find_proper_rotational_axes_polygonal_faces_I(std::vector<Operation> C2s) {
    // the remaining C3 and C5 rotations are orthogonal to pairs of C2 rotations
    // so we take cross products of pairs of C2 rotations and test for C3 and C5 symmetry
    for (unsigned int i = 0; i < C2s.size() - 1; ++i) {
        for (unsigned int j = i + 1; j < C2s.size(); ++j) {
            glm::vec3 axis = glm::cross(C2s[i].get_axis(), C2s[j].get_axis());

            if (glm::length2(axis) == 0) continue;

            for (unsigned int degree = 3; degree <= 5; degree += 2) {  // {3, 5}
                Operation rotation(OperationLabel::Element::ProperRotation, degree, axis);
                this->operation_manager->add_operation(rotation);
            }
        }
    }
}

/**
 * @brief Find improper rotational axes in the structure.
 */
void Symmetry::find_improper_rotational_axes() {
    if (this->get_rotor_class() == RotorClass::Linear) {
        // only S∞ for linear structures
        glm::vec3 axis = glm::column(this->get_principal_axes(), 0);

        Operation imp_rotation(OperationLabel::Element::ImproperRotation, Operation::DEGREE_INF, axis);
        this->operation_manager->add_operation(imp_rotation);
    } else {
        // improper rotational axes are coincident with proper rotational axes, and
        // have degree equal to either n or 2n
        for (Operation& operation : this->operation_manager->get_operations()) {
            if (operation.get_label().get_element() != OperationLabel::Element::ProperRotation) continue;

            for (unsigned int degree_factor = 1; degree_factor <= 2; ++degree_factor) {  // {1, 2}
                unsigned int degree = operation.get_degree() * degree_factor;
                if (degree <= 2) continue;  // S1 = σ, S2 = i

                Operation imp_rotation(OperationLabel::Element::ImproperRotation,
                                       degree, operation.get_axis());
                this->operation_manager->add_operation(imp_rotation);
            }
        }
    }
}

/**
 * @brief Find reflection planes in the structure.
 */
void Symmetry::find_reflection_planes() {
    // infinite reflection planes (∞ σv) in C∞v and D∞d are not tracked here
    if (this->get_rotor_class() == RotorClass::Linear) return;

    // if octahedral or icosahedral symmetry, we can limit the reflection plane
    // search to only include planes with normals coinciding with C2 rotational
    // axes
    bool octahedral_or_icosahedral = false;

    if (this->get_rotor_class() == RotorClass::SphericalTop) {
        unsigned int num_C2s = 0;
        for (Operation& operation : this->operation_manager->get_operations()) {
            if (operation.get_label().get_element() == OperationLabel::Element::ProperRotation &&
                operation.get_degree() == 2) {
                num_C2s++;
            }
        }

        if (num_C2s == 9 || num_C2s == 15) octahedral_or_icosahedral = true;
    }

    if (!octahedral_or_icosahedral) this->find_reflection_planes_normal_to_principal_axes();
    this->find_reflection_planes_normal_to_proper_rotational_axes(octahedral_or_icosahedral);
    if (!octahedral_or_icosahedral) this->find_reflection_planes_in_midpoints();
}

/**
 * @brief Find reflection planes which are normal to the principal axes of
 * the structure.
 */
void Symmetry::find_reflection_planes_normal_to_principal_axes() {
    for (unsigned int i = 0; i < 3; ++i) {
        glm::vec3 normal = glm::column(this->get_principal_axes(), i);
        Operation reflection(OperationLabel::Element::Reflection, normal);
        this->operation_manager->add_operation(reflection);
    }
}

/**
 * @brief Find reflection planes which are normal to proper rotational
 * axes.
 *
 * @param only_C2s whether to only search normal to C2 rotational axes (in
 * case of octahedral and icosahedral symmetry)
 */
void Symmetry::find_reflection_planes_normal_to_proper_rotational_axes(bool only_C2s) {
    for (Operation& operation : this->operation_manager->get_operations()) {
        if (operation.get_label().get_element() != OperationLabel::Element::ProperRotation ||
            (only_C2s && operation.get_degree() != 2)) continue;

        Operation reflection(OperationLabel::Element::Reflection, operation.get_axis());
        this->operation_manager->add_operation(reflection);
    }
}

/**
 * @brief Find reflection planes which pass through midpoints between pairs
 * of atoms of the same element.
 */
void Symmetry::find_reflection_planes_in_midpoints() {
    for (unsigned int i = 0; i < this->structure->get_num_atoms() - 1; ++i) {
        for (unsigned int j = i + 1; j < this->structure->get_num_atoms(); ++j) {
            if (this->structure->get_atomic_number(i) != this->structure->get_atomic_number(j)) continue;

            // calculate midpoint between atoms i and j
            glm::vec3 midpoint = .5f * (this->structure->get_coordinates(i) + this->structure->get_coordinates(j));

            // calculate normal for reflection plane, which is in the plane
            // formed by i and j and perpendicular to the midpoint vector
            glm::vec3 axis = glm::cross(this->structure->get_coordinates(i), this->structure->get_coordinates(j));
            glm::vec3 normal = glm::cross(midpoint, axis);

            if (glm::length2(normal) == 0) continue;
            if (!this->axis_inertially_allowed(normal)) continue;

            Operation reflection(OperationLabel::Element::Reflection, normal);
            this->operation_manager->add_operation(reflection);
        }
    }
}

/**
 * @brief Find the point group with the highest match to the found symmetry
 * operations.
 */
void Symmetry::find_point_group() {
    std::vector<PointGroup> point_groups = PointGroups::point_groups;

    int min_diff = INT_MAX;
    unsigned int best_group_index;

    for (unsigned int i = 0; i < point_groups.size(); ++i) {
        PointGroup& point_group = point_groups[i];
        int diff = point_group.compare_to_symmetry_operations(this->operation_manager->get_operations());

        if (diff >= 0 && diff < min_diff) {
            min_diff = diff;
            best_group_index = i;
        }
    }

    this->point_group = point_groups[best_group_index];
}

/**
 * @brief Find the Cartesian axes of the structure, according to molecular
 * symmetry conventions.
 */
void Symmetry::find_cartesian_axes() {
    unsigned int num_rotations = 0;
    for (Operation& operation : this->operation_manager->get_operations()) {
        if (operation.get_label().get_element() == OperationLabel::Element::ProperRotation)
            num_rotations++;
    }

    if (this->get_rotor_class() == RotorClass::SphericalTop || num_rotations == 0) {
        // if the structure is a spherical top or nonaxial, use the principal axes
        this->assign_principal_axes_to_cartesian_xz_axes();
    } else {
        this->find_z_axis();

        if (this->structure->get_num_atoms() >= 3) {
            // planes in 3D require 3 points to be defined
            glm::vec3 plane_normal = this->find_plane_normal();
            bool is_planar = this->structure_is_planar(plane_normal);

            if (is_planar) {
                this->find_x_axis_planar(plane_normal);
            } else {
                this->find_x_axis_not_planar();
            }
        } else {
            this->pick_arbitrary_x_axis();
        }
    }

    this->orthonormalise_xz_axes();
    this->find_y_axis();
}

/**
 * @brief Assign two of the principal axes of the structure (from the
 * inertial tensor) to the Cartesian x and z axes.
 */
void Symmetry::assign_principal_axes_to_cartesian_xz_axes() {
    this->z_axis = glm::column(this->principal_axes, 0);
    this->x_axis = glm::column(this->principal_axes, 1);
}

/**
 * @brief Find the z axis (principal axis) of the structure.
 */
void Symmetry::find_z_axis() {
    // if the structure is a spherical top, there is no difference between axes
    if (this->get_rotor_class() == RotorClass::SphericalTop) return;

    // search for z axes based on highest degree of rotational axes
    std::vector<glm::vec3> possible_z_axes;

    // find highest degree
    unsigned int max_degree = 0;
    for (Operation& operation : this->operation_manager->get_operations()) {
        if (operation.get_label().get_element() == OperationLabel::Element::ProperRotation &&
            operation.get_degree() > max_degree) {
            max_degree = operation.get_degree();
        }
    }

    // find rotational axes with this degree
    for (Operation& operation : this->operation_manager->get_operations()) {
        if (operation.get_label().get_element() == OperationLabel::Element::ProperRotation &&
            operation.get_degree() == max_degree) {
            possible_z_axes.push_back(operation.get_axis());
        }
    }

    if (possible_z_axes.size() == 1) {
        // only one possibility
        this->z_axis = possible_z_axes[0];
        return;
    }

    // multiple possibilities, so find the axis intersecting with the highest
    // number of atoms
    std::vector<unsigned int> num_intersections_per_axis;
    unsigned int max_num_intersections = 0;
    for (unsigned int i = 0; i < possible_z_axes.size(); ++i) {
        unsigned int num_intersections = 0;

        for (unsigned int j = 0; j < this->structure->get_num_atoms(); ++j) {
            float dot = std::abs(glm::dot(possible_z_axes[i], glm::normalize(this->structure->get_coordinates(j))));
            // TODO move tolerance to a variable/constant
            if (dot > 1 - .02) num_intersections++;
        }

        num_intersections_per_axis.push_back(num_intersections);
        if (num_intersections > max_num_intersections) max_num_intersections = num_intersections;
    }

    // find rotational axes with the maximum number of intersections
    std::vector<glm::vec3> possible_z_axes2;

    for (unsigned int i = 0; i < possible_z_axes.size(); ++i) {
        if (num_intersections_per_axis[i] == max_num_intersections) {
            possible_z_axes2.push_back(possible_z_axes[i]);
        }
    }

    if (possible_z_axes2.size() == 1) {
        // only one possibility
        this->z_axis = possible_z_axes2[0];
        return;
    } else if (possible_z_axes2.size() == 0) return;  // no possibilities

    // finally, prefer the axis that is most parallel with a principal axis
    unsigned int most_parallel_idx;
    float min_diff = INFINITY;

    for (unsigned int i = 0; i < possible_z_axes2.size(); ++i) {
        float this_axis_min_diff = INFINITY;

        for (unsigned int j = 0; j < 3; ++j) {
            glm::vec3 principal_axis = glm::column(this->get_principal_axes(), j);
            float diff = 1 - std::abs(glm::dot(possible_z_axes2[i], principal_axis));

            if (diff < this_axis_min_diff) this_axis_min_diff = diff;
        }

        if (this_axis_min_diff < min_diff) {
            most_parallel_idx = i;
            min_diff = this_axis_min_diff;
        }
    }

    this->z_axis = possible_z_axes2[most_parallel_idx];
}

/**
 * @brief Find the best-fitting plane through all atoms using a singular
 * value decomposition.
 *
 * @return glm::vec3 best-fitting plane
 */
glm::vec3 Symmetry::find_plane_normal() {
    if (this->structure->get_num_atoms() < 3) {
        throw std::runtime_error("Planes can only be found for structures with at least 3 atoms.");
    }

    // implementation based on https://math.stackexchange.com/a/99317

    // set up 3xN matrix of atom coordinates
    Eigen::MatrixXf coordinates(3, this->structure->get_num_atoms());

    for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
        glm::vec3 atom_coordinates = this->structure->get_coordinates(i);
        coordinates(0, i) = atom_coordinates.x;
        coordinates(1, i) = atom_coordinates.y;
        coordinates(2, i) = atom_coordinates.z;
    }

    // compute SVD with thin left singular vector (U)
    Eigen::BDCSVD<Eigen::MatrixXf> svd(coordinates, Eigen::DecompositionOptions::ComputeThinU);

    // the normal of the plane is the left singular vector corresponding to the
    // least singular value. singular values are always sorted in decreasing
    // order (from Eigen docs), so we are looking for the rightmost column
    // (column 2, as U is a 3x3 matrix).
    Eigen::VectorXf e_normal = svd.matrixU().col(2);

    // convert normal to GLM vector
    glm::vec3 normal{e_normal.x(), e_normal.y(), e_normal.z()};

    return normal;
}

/**
 * @brief Determine whether the structure is planar by comparing the
 * positions of the atoms to the best-fitting plane.
 *
 * @param plane_normal best-fitting plane
 * @return true if structure is planar
 * @return false if structure is not planar
 */
bool Symmetry::structure_is_planar(glm::vec3& plane_normal) {
    float sum_dot = 0;

    for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
        // because the best-fitting plane goes through the origin and the
        // normal is a unit vector, the distance between this plane and an atom
        // is equal to the (absolute) dot product
        sum_dot += std::abs(glm::dot(plane_normal, this->structure->get_coordinates(i)));
    }

    // TODO make tolerance variable/constant
    return sum_dot / this->structure->get_num_atoms() < .02;
}

/**
 * @brief Find the x axis of the structure under the assumption that the
 * structure is planar.
 */
void Symmetry::find_x_axis_planar(glm::vec3& plane_normal) {
    // TODO make tolerance variable/constant
    if (glm::dot(plane_normal, this->z_axis) > 1 - .02) {
        // z axis is parallel to plane normal -> perpendicular to plane
        // -> x axis lies in plane and passes through the greatest number of atoms
        glm::vec3 x_axis;
        unsigned int max_num_intersections = 0;
        for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
            glm::vec3 axis = glm::normalize(this->structure->get_coordinates(i));

            // check if axis lies in plane (is possible x axis), continue otherwise
            // TODO make tolerance variable/constant
            if (glm::abs(glm::dot(axis, plane_normal)) > .02) continue;

            unsigned int num_intersections = 0;
            for (unsigned int j = 0; j < this->structure->get_num_atoms(); ++j) {
                float dot = glm::abs(glm::dot(axis, glm::normalize(this->structure->get_coordinates(j))));
                if (dot > 1 - .02) num_intersections++;
            }

            if (num_intersections > max_num_intersections) {
                max_num_intersections = num_intersections;
                x_axis = axis;
            }
        }

        this->x_axis = x_axis;
    } else {
        // z axis lies in plane
        // -> x axis is perpendicular to plane -> parallel to plane normal
        this->x_axis = plane_normal;
    }
}

/**
 * @brief Find the x axis of the structure under the assumption that the
 * structure is not planar.
 */
void Symmetry::find_x_axis_not_planar() {
    // the xz plane should contain as many atoms as possible, so we try all
    // possible xz planes given a fixed z axis and check the number of atoms in
    // each plane.
    glm::vec3 x_axis;
    unsigned int max_num_intersections = 0;

    for (unsigned int i = 0; i < this->structure->get_num_atoms(); ++i) {
        glm::vec3 axis = glm::normalize(this->structure->get_coordinates(i));
        // TODO make tolerance variable/constant
        if (glm::length2(axis) < .02) continue;  // atom is in origin
        if (glm::abs(glm::dot(this->z_axis, axis)) > 1 - .02) continue;  // atom is on z axis

        glm::vec3 plane_normal = glm::normalize(glm::cross(this->z_axis, axis));

        unsigned int num_intersections = 0;
        for (unsigned int j = 0; j < this->structure->get_num_atoms(); ++j) {
            float dot = glm::abs(glm::dot(plane_normal, glm::normalize(this->structure->get_coordinates(j))));
            if (dot < .02) num_intersections++;
        }

        if (num_intersections > max_num_intersections) {
            max_num_intersections = num_intersections;
            x_axis = axis;
        }
    }

    this->x_axis = x_axis;
}

/**
 * @brief Pick an arbitrary x axis for the structure if it is linear.
 */
void Symmetry::pick_arbitrary_x_axis() {
    if (std::abs(this->z_axis.y) < .01 || std::abs(this->z_axis.z) < .01) {
        this->x_axis = glm::vec3(1, 0, 0);
    } else {
        this->x_axis = glm::vec3(0, 1, 0);
    }
}

/**
 * @brief Orthonormalise the x axis with respect to the z axis of the
 * structure using the Gram-Schmidt procedure.
 */
void Symmetry::orthonormalise_xz_axes() {
    // the z axis remains fixed
    this->z_axis = glm::normalize(this->z_axis);

    // Gram-Schmidt
    this->x_axis = glm::normalize(this->x_axis - glm::dot(this->z_axis, this->x_axis) * this->z_axis);
}

/**
 * @brief Find the y axis of the structure using the x and z axes.
 */
void Symmetry::find_y_axis() {
    // right-handed coordinate system
    this->y_axis = glm::cross(this->z_axis, this->x_axis);
}

/**
 * @brief Label the symmetry operations based on the point group and their
 * orientations with respect to the Cartesian axes.
 */
void Symmetry::label_symmetry_operations() {
    // inversions and improper rotational axes don't need labelling
    this->label_proper_rotational_axes();
    this->label_reflection_planes();
}

/**
 * @brief Label the proper rotational axes.
 */
void Symmetry::label_proper_rotational_axes() {
    // proper rotational axes only need additional labels in dihedral and octahedral point groups
    if (this->point_group.get_label().is_dihedral()) this->label_proper_rotational_axes_dihedral();
    if (this->point_group.get_label().is_octahedral()) this->label_proper_rotational_axes_octahedral();
}

/**
 * @brief Label the proper rotational axes for dihedral point groups.
 */
void Symmetry::label_proper_rotational_axes_dihedral() {
    PointGroupLabel point_group_label = this->point_group.get_label();

    for (Operation& operation : this->operation_manager->get_operations()) {
        OperationLabel& operation_label = operation.get_label();

        if (operation_label.get_element() != OperationLabel::Element::ProperRotation) continue;

        // only C2 axes can have an additional label
        if (operation.get_degree() != 2) continue;

        // C2 parallel with z axis has no additional label
        // TODO make tolerance constant/variable
        if (std::abs(glm::dot(operation.get_axis(), this->z_axis)) > 1 - .02) continue;

        if (point_group_label.get_class() == PointGroupLabel::Class::Dd ||
            point_group_label.get_order() % 2 == 1) {
            // Dd point groups and D/Dh point groups with odd n only have C2 and C2'
            operation_label.set_prime(OperationLabel::Prime::Single);
            continue;
        }

        // D/Dh point groups with even n: angle between x axis and C2' is integer multiple of 360°/n
        double theta_x = std::acos(glm::dot(operation.get_axis(), this->x_axis));
        double divisor = 2 * M_PI / point_group_label.get_order();
        double remainder = std::fmod(theta_x, divisor);

        if (remainder <= .25 * divisor | remainder > .75 * divisor) {
            // approximately integer multiple
            operation_label.set_prime(OperationLabel::Prime::Single);
        } else {
            // approximately half-integer multiple
            operation_label.set_prime(OperationLabel::Prime::Double);
        }
    }
}

/**
 * @brief Label the proper rotational axes for octahedral point groups.
 */
void Symmetry::label_proper_rotational_axes_octahedral() {
    for (Operation& operation : this->operation_manager->get_operations()) {
        OperationLabel& operation_label = operation.get_label();

        if (operation_label.get_element() != OperationLabel::Element::ProperRotation) continue;

        // only C2 axes can have an additional label
        if (operation.get_degree() != 2) continue;

        // C2s parallel with principal axes have no additional label
        bool parallel_with_principal_axis = false;
        for (unsigned int j = 0; j < 3; ++j) {
            glm::vec3 principal_axis = glm::column(this->get_principal_axes(), j);

            // TODO make tolerance constant/variable
            if (std::abs(glm::dot(operation.get_axis(), principal_axis)) > 1 - .02) {
                parallel_with_principal_axis = true;
                break;
            }
        }

        if (!parallel_with_principal_axis) {
            operation_label.set_prime(OperationLabel::Prime::Single);
        }
    }
}

/**
 * @brief Label the reflection planes.
 */
void Symmetry::label_reflection_planes() {
    // reflection planes only need additional labels in some point groups
    switch (this->point_group.get_label().get_class()) {
        case PointGroupLabel::Class::Cv:
        case PointGroupLabel::Class::Ch:
        case PointGroupLabel::Class::Cs:
        case PointGroupLabel::Class::Dh:
        case PointGroupLabel::Class::Dd:
            this->label_reflection_planes_cyclic_dihedral();
            break;
        case PointGroupLabel::Class::Td:
        case PointGroupLabel::Class::Th:
            this->label_reflection_planes_tetrahedral();
            break;
        case PointGroupLabel::Class::Oh:
            this->label_reflection_planes_octahedral();
            break;
        default:
            // other point group classes either have reflection planes without
            // additional label (Ih), or no reflection planes at all
            break;
    }
}

/**
 * @brief Label the reflection planes for cyclic and dihedral point groups.
 */
void Symmetry::label_reflection_planes_cyclic_dihedral() {
    PointGroupLabel point_group_label = this->point_group.get_label();

    for (Operation& operation : this->operation_manager->get_operations()) {
        OperationLabel& operation_label = operation.get_label();

        if (operation_label.get_element() != OperationLabel::Element::Reflection) continue;

        // normal parallel with z axis is σv
        // TODO make tolerance constant/variable
        if (std::abs(glm::dot(operation.get_axis(), this->z_axis)) > 1 - .02) {
            operation_label.set_plane(OperationLabel::Plane::Horizontal);
            continue;
        }

        // Dd point groups only have σd
        if (point_group_label.get_class() == PointGroupLabel::Class::Dd) {
            operation_label.set_plane(OperationLabel::Plane::Dihedral);
            continue;
        }

        // point groups with odd n only have σh and σv -> others are all σv
        if (point_group_label.get_order() % 2 == 1) {
            operation_label.set_plane(OperationLabel::Plane::Vertical);
            continue;
        }

        // even n: angle between y axis and normal (xz plane and reflection plane)
        // of σv is integer multiple of 360°/n
        double theta_y = std::acos(glm::dot(operation.get_axis(), this->y_axis));
        double divisor = 2 * M_PI / point_group_label.get_order();
        double remainder = std::fmod(theta_y, divisor);

        if (remainder <= .25 * divisor || remainder > .75 * divisor) {
            // approximately integer multiple
            operation_label.set_plane(OperationLabel::Plane::Vertical);
        } else {
            // approximately half-integer multiple
            if (point_group_label.get_order() == 2) {
                // C2v and D2h use σv' instead of σd as there are no axes to bisect
                operation_label.set_plane(OperationLabel::Plane::Vertical);
                operation_label.set_prime(OperationLabel::Prime::Single);
            } else {
                operation_label.set_plane(OperationLabel::Plane::Dihedral);
            }
        }
    }
}

/**
 * @brief Label the reflection planes for tetrahedral point groups.
 */
void Symmetry::label_reflection_planes_tetrahedral() {
    // all planes in tetrahedral point groups have the same label,
    // depending on the point group
    OperationLabel::Plane plane;

    switch (this->point_group.get_label().get_class()) {
        case PointGroupLabel::Class::Td:
            plane = OperationLabel::Plane::Dihedral;
            break;
        case PointGroupLabel::Class::Th:
            plane = OperationLabel::Plane::Horizontal;
            break;
        default:
            throw std::runtime_error("Unexpected point group class encountered.");
    }

    for (Operation& operation : this->operation_manager->get_operations()) {
        if (operation.get_label().get_element() != OperationLabel::Element::Reflection) continue;
        operation.get_label().set_plane(plane);
    }
}

/**
 * @brief Label the reflection planes for octahedral point groups.
 */
void Symmetry::label_reflection_planes_octahedral() {
    for (Operation& operation : this->operation_manager->get_operations()) {
        OperationLabel& operation_label = operation.get_label();

        if (operation_label.get_element() != OperationLabel::Element::Reflection) continue;

        // planes parallel with principal axes (= normal parallel to another
        // principal axis) are σh
        bool parallel_with_principal_axis = false;
        for (unsigned int j = 0; j < 3; ++j) {
            glm::vec3 principal_axis = glm::column(this->get_principal_axes(), j);

            // TODO make tolerance constant/variable
            if (std::abs(glm::dot(operation.get_axis(), principal_axis)) > 1 - .02) {
                parallel_with_principal_axis = true;
                break;
            }
        }

        if (parallel_with_principal_axis) {
            operation_label.set_plane(OperationLabel::Plane::Horizontal);
        } else {
            operation_label.set_plane(OperationLabel::Plane::Dihedral);
        }
    }
}

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
bool Symmetry::axis_inertially_allowed(glm::vec3& axis) {
    RotorClass rotor_class = this->get_rotor_class();

    // if the structure is a spherical top, every axis is inertially allowed
    if (rotor_class == RotorClass::SphericalTop) return true;

    // if the structure is a symmetric top, the axis must either contain the
    // nondegenerate principal axis or be orthogonal to it
    if (rotor_class == RotorClass::OblateSymmetricTop ||
        rotor_class == RotorClass::ProlateSymmetricTop ||
        rotor_class == RotorClass::Linear) {
        glm::vec3 nondegenerate_axis;
        if (rotor_class == RotorClass::OblateSymmetricTop) {
            nondegenerate_axis = glm::column(this->get_principal_axes(), 2);
        } else if (rotor_class == RotorClass::ProlateSymmetricTop || rotor_class == RotorClass::Linear) {
            nondegenerate_axis = glm::column(this->get_principal_axes(), 0);
        }

        float dot = glm::dot(nondegenerate_axis, axis);

        // TODO move tolerance to a variable/constant
        return dot < .02 || dot > 1 - .02;
    }

    // if the structure is an asymmetric top, the axis must contain at least one
    // of the principal axes
    if (rotor_class == RotorClass::AsymmetricTop) {
        float min_dot = INFINITY;

        for (unsigned int i = 0; i < 3; ++i) {
            glm::vec3 principal_axis = glm::column(this->get_principal_axes(), i);
            float dot = glm::dot(principal_axis, axis);

            if (dot < min_dot) min_dot = dot;
        }

        // TODO move tolerance to a variable/constant
        return min_dot < .02;
    }

    return false;
}

/**
 * @brief Get the principal moments of the structure
 *
 * @return const glm::vec3&
 */
const glm::vec3& Symmetry::get_principal_moments() const {
    return this->principal_moments;
}

/**
 * @brief Get the principal axes of the structure
 *
 * @return const glm::mat3x3&
 */
const glm::mat3x3& Symmetry::get_principal_axes() const {
    return this->principal_axes;
}

/**
 * @brief Get the x axis of the structure
 *
 * @return const glm::vec3&
 */
const glm::vec3& Symmetry::get_x_axis() const {
    return this->x_axis;
}

/**
 * @brief Get the y axis of the structure
 *
 * @return const glm::vec3&
 */
const glm::vec3& Symmetry::get_y_axis() const {
    return this->y_axis;
}

/**
 * @brief Get the z axis of the structure
 *
 * @return const glm::vec3&
 */
const glm::vec3& Symmetry::get_z_axis() const {
    return this->z_axis;
}

/**
 * @brief Get the cartesian axes of the structure
 *
 * @return const glm::mat3x3
 */
const glm::mat3x3 Symmetry::get_cartesian_axes() const {
    return glm::mat3x3(this->x_axis, this->y_axis, this->z_axis);
}

/**
 * @brief Get the rotor class of the structure
 *
 * @return const RotorClass
 */
const RotorClass Symmetry::get_rotor_class() const {
    return this->rotor_class;
}

/**
 * @brief Get the operation manager object
 *
 * @return const std::shared_ptr<OperationManager>&
 */
const std::shared_ptr<OperationManager>& Symmetry::get_operation_manager() const {
    return this->operation_manager;
}

/**
 * @brief Get the point group of the structure
 *
 * @return const PointGroup&
 */
const PointGroup& Symmetry::get_point_group() const {
    return this->point_group;
}
