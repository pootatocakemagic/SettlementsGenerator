import pandas as pd
import os
from lib.rolls import *

class SettlementGenerator:
    def __init__(self, csv_path):
        if os.path.isfile(csv_path):
            self.csv_path = csv_path
        else:
            raise NameError(f'Указан неверный путь при инициализации класса SettlementGenerator. '
                            f'Путь {csv_path} не существует.')
        self.modifiers = {}
        self.txt_report = ''
        self.md_report = ''
        self.tables = {}
        self.current_table_name = ''
        self.is_modifiers = False
        self.current_modifier_name = ''
        self.class_field_modifier = []
        self.usage_modifier = ''
        self.save_generate = ''
        self.use_generate = ''
        self.counters = 1

    def generate_settlement(self):
        settlement_csv = pd.read_csv(self.csv_path)
        for line in range(len(settlement_csv)):
            global_name = settlement_csv['global_name'][line]
            local_name = settlement_csv['local_name'][line]
            dice_fields = settlement_csv['dice_fields'][line]
            table_roll = settlement_csv['table_roll'][line]
            class_fields = settlement_csv['class_fields'][line]
            class_fields_modifiers = settlement_csv['class_fields_modifiers'][line]
            usage_modifier = settlement_csv['usage_modifier'][line]
            save_generate = settlement_csv['save_generate'][line]
            use_generate = settlement_csv['use_generate'][line]
            counters = settlement_csv['counters'][line]
            self.analyze_global_name(global_name)
            self.analyze_local_name(local_name, class_fields, usage_modifier, save_generate, use_generate, counters)
            self.analyze_tables(dice_fields, table_roll, class_fields_modifiers)
        self.generate_reports()

    def analyze_tables(self, dice_fields, table_roll, class_fields_modifiers):
        if self.use_generate:
            if not pd.isnull(table_roll):
                face, modifier = table_roll.split(';')
                dice_roll = roll_dice(int(face), self.modifiers[modifier])
                self.txt_report += f' {str(dice_roll)}.\n'
                self.modifiers[self.class_field_modifier[0]] = dice_roll
            else:
                self.use_generate = False
            return
        if self.current_table_name:
            if not pd.isnull(dice_fields):
                self.tables[self.current_table_name][dice_fields] = table_roll
                if self.class_field_modifier:
                    self.tables[self.current_table_name][dice_fields] += f"${' '.join(str(class_fields_modifiers).split(';'))}"

    def reset(self):
        self.current_table_name = ''
        self.tables = {}

    def analyze_global_name(self, global_name):
        if not pd.isnull(global_name):
            self.generate_reports()
            self.txt_report += f"\n------\n{global_name}\n------\n\n"
            self.md_report += f"\n# {global_name}\n"
            self.reset()

    def analyze_local_name(self, local_name, class_fields, usage_modifier, save_generate, use_generate, counters):


        if ':' in str(local_name):
            self.generate_reports()
            self.txt_report += f"{local_name} "
            self.md_report += f"**{local_name}** "
            self.reset()
            if not pd.isnull(class_fields):
                self.class_field_modifier = class_fields.split(';')
            else:
                self.class_field_modifier = []
            if not pd.isnull(usage_modifier):
                self.usage_modifier = usage_modifier
            else:
                self.usage_modifier = ''
            if not pd.isnull(save_generate):
                self.save_generate = save_generate
            else:
                self.save_generate = ''
            if not pd.isnull(use_generate):
                self.use_generate = use_generate
            else:
                self.use_generate = ''
            if not pd.isnull(counters):
                self.counters = int(self.modifiers[counters])
            else:
                self.counters = 1
        elif not pd.isnull(local_name):
            self.tables[local_name] = {}
            self.current_table_name = local_name
        else:
            if not pd.isnull(class_fields):
                class_fields = class_fields.replace(' ', '')
                if class_fields:
                    self.class_field_modifier = class_fields.split(';')

    def generate_reports(self):
        if not self.tables:
            return
        if self.use_generate:
            return
        if self.save_generate:
            position = 1
            if ';' in self.save_generate:

                # print(self.save_generate.split([';']), self.save_generate.split([';']), self.save_generate)
                position += int(self.save_generate.split(';')[1])
                self.save_generate = self.save_generate.split(';')[0]
        name_modifiers = []
        value_modifiers = 0
        #определяем размер бросаемого дайса
        for _ in range(self.counters):
            dice_size = int(list(self.tables['1'].keys())[-1].split('-')[-1])
            #применяем модификаторы к броску
            if self.usage_modifier and self.usage_modifier in self.modifiers.keys():
                dice_roll = max(1, min(dice_size, roll_dice(dice_size, self.modifiers[self.usage_modifier])))
            else:
                dice_roll = roll_dice(dice_size)
            #добавляем текст из таблицы в общий отчёт

            for key in self.tables['1'].keys():
                borders = key.split('-')
                if int(borders[0]) <= dice_roll <= int(borders[-1]):
                    if self.save_generate:
                        self.modifiers[self.save_generate] = position
                    text = self.tables['1'][key].split('$')[0]
                    if '&' in text:
                        name_modifiers = self.tables['1'][key].split('&')[1].split(';')
                        text = self.tables['1'][key].split('&')[0]
                    if len(self.tables.keys()) > 1:
                        for key1 in list(self.tables.keys())[:-1]:
                            key1 = str(key1)
                            new_borders = str(key1).split('_')
                            if int(new_borders[1]) <= dice_roll <= int(new_borders[2]):
                                sup_dice_size = int(list(self.tables[key1].keys())[-1].split('-')[-1])
                                sup_dice_roll = roll_dice(sup_dice_size)
                                for key2 in self.tables[key1]:
                                    extra_borders = str(key2).split('-')
                                    if int(extra_borders[0]) <= sup_dice_roll <= int(extra_borders[-1]):
                                        new_text = self.tables[key1][key2]
                                        if '&' in new_text:
                                            value_modifiers = int(new_text.split('&')[1])
                                            new_text = new_text.split('&')[0]
                                            for mds in name_modifiers:
                                                if mds in self.modifiers.keys():
                                                    self.modifiers[mds] += value_modifiers
                                                else:
                                                    self.modifiers[mds] = value_modifiers

                                        text += f' {new_text}'
                    text += '\n'
                    self.txt_report += text
                    for i, modifier in enumerate(self.class_field_modifier):
                        modifiers = self.tables['1'][key].split('$')[-1]

                        if modifier not in self.modifiers.keys():
                            self.modifiers[modifier] = int(modifiers.split(' ')[i])
                        else:
                            self.modifiers[modifier] += int(modifiers.split(' ')[i])

                if self.save_generate:
                    position += 1



        pass
if __name__ == '__main__':

    path_trading_post = 'D:\\PycharmProjects\\generator_settlements\\csv\\trading_post.csv'
    path_village = 'D:\\PycharmProjects\\generator_settlements\\csv\\villages.csv'
    path_town = 'D:\\PycharmProjects\\generator_settlements\\csv\\towns.csv'
    SG = SettlementGenerator(path_village)
    SG.generate_settlement()
    print(SG.txt_report)
    print(SG.modifiers)

