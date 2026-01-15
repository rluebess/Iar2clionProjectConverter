# -*- coding: utf-8 -*-

""" CMake generation module
    @file
"""

import os
import platform
import datetime
from jinja2 import Environment, FileSystemLoader


class CMake (object):

    def __init__(self, project, path):

        self.path = path
        self.project = project
        self.context = {}

    def populateCMake(self, compiler):
        """ Generate CMakeLists.txt file for building the project
        """
        fpu = 'VFPv4_sp'
        core = ''

        if 'STM32F0' in self.project['chip']:
            core = 'Cortex-M0'
        elif 'STM32F1' in self.project['chip']:
            core = 'Cortex-M3'
        elif 'STM32F2' in self.project['chip']:
            core = 'Cortex-M3'
        elif 'STM32F3' in self.project['chip']:
            core = 'Cortex-M4'
        elif 'STM32F4' in self.project['chip']:
            core = 'Cortex-M4'
        elif 'STM32F7' in self.project['chip']:
            core = 'Cortex-M7'
        elif 'STM32L0' in self.project['chip']:
            core = 'Cortex-M0plus'
        elif 'STM32L1' in self.project['chip']:
            core = 'Cortex-M3'
        elif 'STM32L4' in self.project['chip']:
            core = 'Cortex-M4'
        elif 'STR912F' in self.project['chip'] or 'STR91x' in self.project['chip']:
            core = 'ARM966E-S'
            fpu = 'None'
        else:
            core = 'unknown'
            print("Warning: CPU core could not be determined for chip: " + self.project['chip'])

        if compiler == "iar":
            if 'STR912' in self.project['chip']:
                template_file = 'CMakeLists_iar_STR91.tmpl'
            else:
                template_file = 'CMakeLists_iar.tmpl'
            with open(template_file, 'r', encoding='utf-8') as file:
                file_content = file.read()
        elif compiler == "clang":
            with open('CMakeLists.tmpl', 'r', encoding='utf-8') as file:
                file_content = file.read()

        # Replace the search string with the replace string
        updated_content = file_content.replace(
            "%project_name%", self.project['name'])
        updated_content = updated_content.replace(
            "%chip%", self.project['chip'])
        updated_content = updated_content.replace("%core%", core)
        updated_content = updated_content.replace("%fpu%", fpu)
        updated_content = updated_content.replace(
            "%dlib_config%", self.project['dlib_config'])
        updated_content = updated_content.replace(
            "%dlib_config%", self.project['dlib_config'])
        updated_content = self.replaceOrDelete(
            updated_content, "%diag_suppress%", self.project['diag_suppress'])
        updated_content = self.replaceOrDelete(
            updated_content, "%diag_error%", self.project['diag_error'])
        updated_content = updated_content.replace(
            "%sources_base%", self.project['srcs_base'])
        if 'toolkit_dir' in self.project:
            updated_content = updated_content.replace(
                "%toolkit_dir%", self.project['toolkit_dir'])
        else:
            updated_content = updated_content.replace(
                "%toolkit_dir%", "UNDEFINED-PLEASE EDIT")

        replace_string = ''
        replace_string_lib = ''
        for string in self.project['srcs']:
            if string.endswith('.a'):
                replace_string_lib += "\t\"${SOURCES_BASE_PATH}" + \
                    string + "\"\n"
            else:
                replace_string += "    ${SOURCES_BASE_PATH}" + string + "\n"
        updated_content = updated_content.replace(
            "%source_file%", replace_string)
        updated_content = updated_content.replace(
            "%lib_files%", replace_string_lib)

        replace_string = ''
        for string in self.project['incs']:
            replace_string += "    ${SOURCES_BASE_PATH}" + string + "\n"
        updated_content = updated_content.replace(
            "%include_dir%", replace_string)
        replace_string = ''
        for string in self.project['defs']:
            replace_string += "    " + string + "\n"
        updated_content = updated_content.replace(
            "%preprocessor_defines%", replace_string)
        updated_content = updated_content.replace(
            "%linker_icf%", self.project['linker_icf'])
        replace_string = ''
        for string in self.project['linker_symbols']:
            if isinstance(string, str):
                replace_string += "--keep " + string + "\n"
        updated_content = updated_content.replace(
            "%linker_symbol%", replace_string)

        # Write the updated content back to the file
        output_path = os.path.join(os.path.dirname(self.path), 'CMakeLists.txt')
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)

    def replaceOrDelete(self, content, target_string, replacement):
        if (replacement == ''):
            # Split the content into lines
            lines = content.splitlines()

            # Filter out lines that contain the specified string
            filtered_lines = [
                line for line in lines if target_string not in line]

            # Join the remaining lines back into a single string
            content = '\n'.join(filtered_lines)
        else:
            content = content.replace(target_string, replacement)
        return content

    def populateCMake_old(self):
        """ Generate CMakeList.txt file for building the project
        """

        # For debug run cmake -DCMAKE_BUILD_TYPE=Debug or Release
        cmake = {}
        # fpu = '-mfpu=fpv5-sp-d16 -mfloat-abi=softfp'
        fpu = ''

        core = ''

        if 'STM32F0' in self.project['chip']:
            core = '-mcpu=cortex-m0'
        elif 'STM32F1' in self.project['chip']:
            core = '-mcpu=cortex-m3'
        elif 'STM32F2' in self.project['chip']:
            core = '-mcpu=cortex-m3'
        elif 'STM32F3' in self.project['chip']:
            core = '-mcpu=cortex-m4'
        elif 'STM32F4' in self.project['chip']:
            core = '-mcpu=cortex-m4'
        elif 'STM32F7' in self.project['chip']:
            core = '-mcpu=cortex-m7'
        elif 'STM32L0' in self.project['chip']:
            core = '-mcpu=cortex-m0plus'
        elif 'STM32L1' in self.project['chip']:
            core = '-mcpu=cortex-m3'
        elif 'STM32L4' in self.project['chip']:
            core = '-mcpu=cortex-m4'

        cmake['version'] = '3.1'
        cmake['project'] = self.project['name']
        cmake['incs'] = []
        for inc in self.project['incs']:
            cmake['incs'].append(inc)
        cmake['srcs'] = []

        i = 0

        cmake['files'] = []
        cmake['ass'] = []

        for file in self.project['srcs']:
            if file.endswith('.c') or file.endswith('.h') or file.endswith('.cpp'):
                cmake['files'].append(
                    {'path': file, 'var': 'SRC_FILE' + str(i)})
                i = i+1

        for file in self.project['files']:
            print('Assembly added ' + file)
            cmake['ass'].append({'path': file})
            cmake['files'].append({'path': file, 'var': 'SRC_FILE' + str(i)})
            i = i+1

        cmake['cxx'] = 'false'

        cmake['c_flags'] = '-g -Wextra -Wshadow -Wimplicit-function-declaration -Wredundant-decls -Wmissing-prototypes -Wstrict-prototypes -fno-common -ffunction-sections -fdata-sections -MD -Wall -Wundef -mthumb ' + core + ' ' + fpu

        cmake['cxx_flags'] = '-Wextra -Wshadow -Wredundant-decls  -Weffc++ -fno-common -ffunction-sections -fdata-sections -MD -Wall -Wundef -mthumb ' + core + ' ' + fpu

        cmake['asm_flags'] = '-g -mthumb ' + core + \
            ' ' + fpu  # + ' -x assembler-with-cpp'
        cmake['linker_flags'] = '-g -Wl,--gc-sections -Wl,-Map=' + \
            cmake['project'] + '.map -mthumb ' + core + ' ' + fpu
        cmake['linker_script'] = 'STM32FLASH.ld'
        cmake['linker_path'] = ''

        self.linkerScript('STM32FLASH.ld', os.path.join(
            os.path.dirname(self.path), 'STM32FLASH.ld'))

        cmake['oocd_target'] = 'stm32f3x'
        cmake['defines'] = []
        for define in self.project['defs']:
            cmake['defines'].append(define)

        cmake['libs'] = []

        self.context['cmake'] = cmake

        abspath = os.path.abspath(os.path.join(os.path.dirname(self.path), 'CMakeLists.txt'))
        self.generateFile('CMakeLists.txt', abspath)

        print('Created file CMakeLists.txt [{}]'.format(abspath))

#    def generateFile (self, pathSrc, pathDst='', author='Pegasus', version='v1.0.0', licence='licence.txt', template_dir='../PegasusTemplates'):
    def generateFile(self, pathSrc, pathDst='', author='Pegasus', version='v1.0.0', licence='licence.txt', template_dir='.'):

        if (pathDst == ''):
            pathDst = pathSrc

        self.context['file'] = os.path.basename(str(pathSrc))
        self.context['author'] = author
        self.context['date'] = datetime.date.today().strftime('%d, %b %Y')
        self.context['version'] = version
        self.context['licence'] = licence

        env = Environment(loader=FileSystemLoader(template_dir),
                          trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(str(pathSrc))

        generated_code = template.render(self.context)

        if platform.system() == 'Windows':

            with open(pathDst, 'w', encoding='utf-8') as f:
                f.write(generated_code)

        elif platform.system() == 'Linux':

            with open(pathDst, 'w', encoding='utf-8') as f:
                f.write(generated_code)
        else:
            # Different OS than Windows or Linux
            pass

    def linkerScript(self, pathSrc, pathDst='', template_dir='.'):
        #    def linkerScript(self,pathSrc, pathDst='',template_dir='.../PegasusTemplates'):

        if (pathDst == ''):
            pathDst = pathSrc

        self.context['file'] = os.path.basename(str(pathSrc))
        self.context['flash'] = '64'
        self.context['ram'] = '8'

        env = Environment(loader=FileSystemLoader(template_dir),
                          trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(str(pathSrc))

        generated_code = template.render(self.context)

        if platform.system() == 'Windows':

            with open(pathDst, 'w', encoding='utf-8') as f:
                f.write(generated_code)

        elif platform.system() == 'Linux':

            with open(pathDst, 'w', encoding='utf-8') as f:
                f.write(generated_code)
        else:
            # Different OS than Windows or Linux
            pass
