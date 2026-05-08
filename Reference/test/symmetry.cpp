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

#include <memory>
#include <vector>
#include <boost/test/unit_test.hpp>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_access.hpp>
#include "../src/structure.h"
#include "../src/symmetry/rotor_class.h"
#include "../src/symmetry/symmetry.h"
#include "utils.h"

BOOST_AUTO_TEST_SUITE(symmetry);

BOOST_AUTO_TEST_CASE(principal_axes) {
    std::string file = resolve_path("test/files/ammonia.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    glm::vec3 principal_moments = symmetry.get_principal_moments();
    glm::vec3 expected_principal_moments{1.65324, 1.65324, 2.62436};
    BOOST_TEST(glm::all(glm::epsilonEqual(principal_moments, expected_principal_moments, 1e-5f)));

    glm::mat3x3 principal_axes = symmetry.get_principal_axes();
    glm::mat3x3 expected_principal_axes{
        1, 0, 0,
        0, 1, 0,
        0, 0, 1
    };
    for (unsigned int i = 0; i < 3; ++i) {
        BOOST_TEST(glm::all(glm::epsilonEqual(glm::column(principal_axes, i), glm::column(expected_principal_axes, i), 1e-6f)));
    }
}

BOOST_AUTO_TEST_CASE(rotor_asymmetric_top) {
    std::string file = resolve_path("test/files/thionyl-chloride.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    BOOST_TEST(symmetry.get_rotor_class() == RotorClass::AsymmetricTop);
}

BOOST_AUTO_TEST_CASE(rotor_oblate_symmetric_top) {
    std::string file = resolve_path("test/files/benzene.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    BOOST_TEST(symmetry.get_rotor_class() == RotorClass::OblateSymmetricTop);
}

BOOST_AUTO_TEST_CASE(rotor_prolate_symmetric_top) {
    std::string file = resolve_path("test/files/iron-pentacarbonyl.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    BOOST_TEST(symmetry.get_rotor_class() == RotorClass::ProlateSymmetricTop);
}

BOOST_AUTO_TEST_CASE(rotor_linear) {
    std::string file = resolve_path("test/files/carbon-dioxide.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    BOOST_TEST(symmetry.get_rotor_class() == RotorClass::Linear);
}

BOOST_AUTO_TEST_CASE(rotor_spherical_top) {
    std::string file = resolve_path("test/files/adamantane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    BOOST_TEST(symmetry.get_rotor_class() == RotorClass::SphericalTop);
}

BOOST_AUTO_TEST_CASE(axes_benzene) {
    std::string file = resolve_path("test/files/benzene.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    std::vector<glm::vec3> expected_axes{
        {0, 1, 0},
        {-1, 0, 0},
        {0, 0, 1}
    };
    std::vector<glm::vec3> axes{symmetry.get_x_axis(), symmetry.get_y_axis(), symmetry.get_z_axis()};
    for (unsigned int i = 0; i < 3; ++i) {
        BOOST_TEST(glm::all(glm::epsilonEqual(axes[i], expected_axes[i], 1e-6f)));
    }
}

BOOST_AUTO_TEST_CASE(axes_boric_acid) {
    std::string file = resolve_path("test/files/boric-acid.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    std::vector<glm::vec3> expected_axes{
        {.007302, .999973, 0},
        {-.999973, .007302, 0},
        {0, 0, 1}
    };
    std::vector<glm::vec3> axes{symmetry.get_x_axis(), symmetry.get_y_axis(), symmetry.get_z_axis()};
    for (unsigned int i = 0; i < 3; ++i) {
        BOOST_TEST(glm::all(glm::epsilonEqual(axes[i], expected_axes[i], 1e-6f)));
    }
}

BOOST_AUTO_TEST_CASE(axes_carbon_dioxide) {
    std::string file = resolve_path("test/files/carbon-dioxide.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    glm::vec3 expected_z_axis{0, 0, 1};
    BOOST_TEST(glm::all(glm::epsilonEqual(expected_z_axis, symmetry.get_z_axis(), 1e-6f)));

    // exact x and y axes are irrelevant, as long as they are orthonormal
    BOOST_TEST(glm::abs(glm::dot(symmetry.get_x_axis(), symmetry.get_y_axis())) < 1e-6f);
    BOOST_TEST(glm::abs(glm::dot(symmetry.get_x_axis(), symmetry.get_z_axis())) < 1e-6f);
}

BOOST_AUTO_TEST_CASE(axes_cyclooctatetraene) {
    std::string file = resolve_path("test/files/cyclooctatetraene.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    std::vector<glm::vec3> expected_axes{
        {.390958, .920408, 0},
        {-.920408, .390958, 0},
        {0, 0, 1}
    };
    std::vector<glm::vec3> axes{symmetry.get_x_axis(), symmetry.get_y_axis(), symmetry.get_z_axis()};
    for (unsigned int i = 0; i < 3; ++i) {
        BOOST_TEST(glm::all(glm::epsilonEqual(axes[i], expected_axes[i], 1e-6f)));
    }
}

BOOST_AUTO_TEST_CASE(axes_ferrocene_eclipsed) {
    std::string file = resolve_path("test/files/ferrocene-eclipsed.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    std::vector<glm::vec3> expected_axes{
        {0, 1, 0},
        {1, 0, 0},
        {0, 0, -1}
    };
    std::vector<glm::vec3> axes{symmetry.get_x_axis(), symmetry.get_y_axis(), symmetry.get_z_axis()};
    for (unsigned int i = 0; i < 3; ++i) {
        BOOST_TEST(glm::all(glm::epsilonEqual(axes[i], expected_axes[i], 1e-6f)));
    }
}

BOOST_AUTO_TEST_CASE(axes_water) {
    std::string file = resolve_path("test/files/water.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    std::vector<glm::vec3> expected_axes{
        {-1, 0, 0},
        {0, -1, 0},
        {0, 0, 1}
    };
    std::vector<glm::vec3> axes{symmetry.get_x_axis(), symmetry.get_y_axis(), symmetry.get_z_axis()};
    for (unsigned int i = 0; i < 3; ++i) {
        BOOST_TEST(glm::all(glm::epsilonEqual(axes[i], expected_axes[i], 1e-6f)));
    }
}

BOOST_AUTO_TEST_SUITE_END();
