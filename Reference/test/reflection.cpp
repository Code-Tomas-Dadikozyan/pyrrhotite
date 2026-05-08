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
#include <glm/gtc/epsilon.hpp>
#include "../src/structure.h"
#include "../src/symmetry/symmetry.h"
#include "../src/symmetry/operations/operation.h"
#include "../src/symmetry/operations/operation_label.h"
#include "utils.h"

BOOST_AUTO_TEST_SUITE(reflection)

BOOST_AUTO_TEST_CASE(bicyclooctane) {
    std::string file = resolve_path("test/files/bicyclooctane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto reflections = symmetry.get_operation_manager()->get_reflections();

    BOOST_TEST(reflections.size() == 0);
}

BOOST_AUTO_TEST_CASE(cubane) {
    std::string file = resolve_path("test/files/cubane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto reflections = symmetry.get_operation_manager()->get_reflections();

    BOOST_TEST(reflections.size() == 9);

    std::vector<glm::vec3> expected_normals{
        {1, 0, 0},
        {0, 1, 0},
        {0, 0, 1},
        {.707107, .707107, 0},
        {-.707107, .707107, 0},
        {.707107, 0, .707107},
        {-.707107, 0, .707107},
        {0, .707107, .707107},
        {0, .707107, -.707107}
    };
    unsigned int matched = 0;

    for (auto reflection : reflections) {
        for (auto normal : expected_normals) {
            if (glm::all(glm::epsilonEqual(reflection.get_axis(), normal, 1e-6f))) matched++;
        }
    }

    BOOST_TEST(matched == 9);
}

BOOST_AUTO_TEST_CASE(dodecahydrododecaborate) {
    std::string file = resolve_path("test/files/dodecahydrododecaborate.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto reflections = symmetry.get_operation_manager()->get_reflections();

    BOOST_TEST(reflections.size() == 15);
}

BOOST_AUTO_TEST_CASE(ferrocene_eclipsed) {
    std::string file = resolve_path("test/files/ferrocene-eclipsed.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto reflections = symmetry.get_operation_manager()->get_reflections();

    BOOST_TEST(reflections.size() == 6);

    std::vector<glm::vec3> expected_normals{
        {0, 0, -1},
        {-1, 0, 0},
        {.809017, .587785, 0},
        {-.309017, -.951057, 0},
        {-.309017, .951057, 0},
        {-.809017, .587785, 0}
    };
    unsigned int matched = 0;

    for (auto reflection : reflections) {
        for (auto normal : expected_normals) {
            if (glm::all(glm::epsilonEqual(reflection.get_axis(), normal, 1e-6f))) matched++;
        }
    }

    BOOST_TEST(matched == 6);
}

BOOST_AUTO_TEST_CASE(methane) {
    std::string file = resolve_path("test/files/methane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto reflections = symmetry.get_operation_manager()->get_reflections();

    BOOST_TEST(reflections.size() == 6);

    std::vector<glm::vec3> expected_normals{
        {.707107, .707107, 0},
        {-.707107, .707107, 0},
        {.707107, 0, .707107},
        {-.707107, 0, .707107},
        {0, .707107, .707107},
        {0, -.707107, .707107}
    };
    unsigned int matched = 0;

    for (auto reflection : reflections) {
        for (auto normal : expected_normals) {
            if (glm::all(glm::epsilonEqual(reflection.get_axis(), normal, 1e-6f))) matched++;
        }
    }

    BOOST_TEST(matched == 6);
}

BOOST_AUTO_TEST_CASE(octasulfur) {
    std::string file = resolve_path("test/files/octasulfur.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto reflections = symmetry.get_operation_manager()->get_reflections();

    BOOST_TEST(reflections.size() == 4);

    std::vector<glm::vec3> expected_normals{
        {1, 0, 0},
        {0, 1, 0},
        {-.707107, .707107, 0},
        {.707107, .707107, 0}
    };
    unsigned int matched = 0;

    for (auto reflection : reflections) {
        for (auto normal : expected_normals) {
            if (glm::all(glm::epsilonEqual(reflection.get_axis(), normal, 1e-6f))) matched++;
        }
    }

    BOOST_TEST(matched == 4);
}

BOOST_AUTO_TEST_CASE(pentaborane_9) {
    std::string file = resolve_path("test/files/pentaborane-9.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto reflections = symmetry.get_operation_manager()->get_reflections();

    BOOST_TEST(reflections.size() == 4);

    std::vector<glm::vec3> expected_normals{
        {1, 0, 0},
        {0, 1, 0},
        {-.707107, .707107, 0},
        {.707107, .707107, 0}
    };
    unsigned int matched = 0;

    for (auto reflection : reflections) {
        for (auto normal : expected_normals) {
            if (glm::all(glm::epsilonEqual(reflection.get_axis(), normal, 1e-6f))) matched++;
        }
    }

    BOOST_TEST(matched == 4);
}

BOOST_AUTO_TEST_CASE(thionyl_chloride) {
    std::string file = resolve_path("test/files/thionyl-chloride.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto reflections = symmetry.get_operation_manager()->get_reflections();

    BOOST_TEST(reflections.size() == 1);
    BOOST_TEST(glm::all(glm::epsilonEqual(reflections[0].get_axis(), glm::vec3(0, 0, 1), 1e-8f)));
}

BOOST_AUTO_TEST_CASE(trans_azobenzene) {
    std::string file = resolve_path("test/files/trans-azobenzene.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto reflections = symmetry.get_operation_manager()->get_reflections();

    BOOST_TEST(reflections.size() == 1);
    BOOST_TEST(glm::all(glm::epsilonEqual(reflections[0].get_axis(), glm::vec3(0, 0, 1), 1e-8f)));
}

BOOST_AUTO_TEST_SUITE_END();
