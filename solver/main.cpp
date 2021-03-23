#include "gooo.hpp"
#include "state.hpp"

int main()
{
	State state(3);
	state.print();

	std::vector<int> sequence = {0, 1, 1, 1, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 2, 0, 0, 0, 0, 0};
	for (size_t index = 0; index < sequence.size(); ++index) {
		if (!state.move(sequence[index])) {
			std::cout << "ERROR!\n";
			break;
		}
		std::cout << state << "\n";

		state.print();
		std::vector<int> moves = state.getPossibleMoves();

		if (!moves.empty()) {
			std::cout << "Possible moves: " << moves[0];
			for (size_t move = 1; move < moves.size(); ++move) {
				std::cout << ", " <<  moves[move];
			}
			std::cout << "\n\n";
		} else {
			std::cout << "No moves available.\n\n";
		}

		if (state.end) {
			std::cout << "Game has ended with " << state.points << " point(s).\n";
		}
	}

	return 0;
}
