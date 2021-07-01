from copy import deepcopy

MAX_STEPS = 100

EPSILON = '*epsilon*'


def find_char_from_list(string, items):
    for c in string:
        if (c in items):
            return True
    return False


class ParseGrammar:
    def __init__(self, file):
        f = open(file)
        read_lines = False
        production_lines = []
        for line in f.readlines():
            parsed_line = line.replace(
                "\n", "").replace("epsilon", "*epsilon*")
            if parsed_line[0] == 'P':
                read_lines = True
                continue

            if parsed_line[0] == '}':
                read_lines = False
                self.P = self.parse_productions_from_lines(production_lines)
                continue

            if read_lines:
                production_lines.append(parsed_line.replace(" ", ""))

            if parsed_line == "":
                continue

            if parsed_line[0] == 'N' and not read_lines:
                self.N = self.parse_set_from_line(parsed_line)

            if parsed_line[0] == 'T' and not read_lines:
                self.T = self.parse_set_from_line(parsed_line)

            if parsed_line[0] == 'S' and not read_lines:
                self.S = parsed_line.split("=")[1].replace(" ", "")

        f.close()

    def parse_set_from_line(self, line):
        return line.split('=')[1].replace(" ", "")[1:-1].split(",")

    def parse_productions_from_lines(self, lines):
        a_map = {}
        for l in lines:
            [key, value] = l.split('->')
            a_map[str(key)] = value.split('|')
        return a_map

    def get_params(self):
        return [self.N, self.T, self.P, self.S]


class Generation:
    def __init__(self, state):
        self.string = str(state)
        self.state = state
        self.steps = []

    def produce(self, production):
        self.string = self.string.replace(self.state, production, 1)
        self.steps.append(self.string)

        if (len(self.steps) > MAX_STEPS):
            return False

        return True

    def set_next_state(self, P):
        current_min = 10000000
        self.state = ""
        for p in P:
            m = self.string.find(p)
            if (m >= 0 and m < current_min):
                current_min = m
                self.state = p

    def done(self, N):
        return not find_char_from_list(self.string, N)

    def remove_epsilon(self):
        self.string = self.string.replace(EPSILON, "")

    def get_steps_string(self):
        return ' -> '.join(self.steps)


class Grammar:

    def __init__(self, N, T, P, S, name="results"):
        self.N = N
        self.T = T
        self.P = P
        self.S = S

        self.p_generations = []
        self.done = []

        self.name = name

    def identify(self):
        tipo = 3
        hasEpsilon = []
        for key, value in self.P.items():
            if find_char_from_list(key, self.T):
                tipo = min(tipo, 1)
                break

            for p in value:
                if p == EPSILON and key not in hasEpsilon:
                    hasEpsilon.append(key)

                if (tipo > 1 and find_char_from_list(p, hasEpsilon)):
                    tipo = 1

                if (tipo == 3):
                    if (p == EPSILON):
                        continue
                    if (len(p) == 1 and p[0] in self.T):
                        continue
                    elif (len(p) == 2 and p[0] in self.T and p[1] in self.N):
                        continue
                    else:
                        tipo = 2

                if (tipo == 1):
                    if (len(key) < len(p) and p != EPSILON):
                        tipo = 0
                        break

        if tipo == 3:
            return "Regular"
        elif tipo == 2:
            return "Livre de Contexto"
        elif tipo == 1:
            return "Sensível ao Contexto"
        else:
            return "Irrestrita"

    def step(self, generation):
        current_production = self.get_production(generation.state)

        for p in current_production:
            gen = deepcopy(generation)
            if (not gen.produce(p)):
                continue

            if (gen.done(self.N)):
                gen.remove_epsilon()
                self.done.append(gen)
            else:
                gen.set_next_state(self.P.keys())
                self.p_generations.append(gen)

    def get_production(self, state):
        return self.P[str(state)]

    def generate(self, max_count=100, print_results=True):
        self.p_generations.append(Generation(self.S))

        while(len(self.p_generations) > 0 and len(self.done) < max_count):
            self.current_generation = self.p_generations.pop(0)

            self.step(self.current_generation)

        if (print_results):
            self.print_results()
        else:
            return self.done

    def print_results(self):
        file = open(f'results/{self.name}.txt', 'w+')
        for i in range(len(self.done)):
            file.write(
                f'{i+1}: {self.done[i].string} ({len(self.done[i].string)}) = {self.done[i].get_steps_string()} \n')
        file.close()


parser = ParseGrammar("teste.txt")
g = Grammar(*parser.get_params(), "nm leq pq'")
print(g.identify())
g.generate()
