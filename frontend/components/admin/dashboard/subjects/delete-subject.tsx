import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
	DialogClose,
} from "@/components/ui/dialog";
import {
	X,
	AlertTriangle,
	ShieldAlert,
} from "lucide-react";

import { educationService } from "@/services/subjects.service";
import { Button } from "@/components/ui/button";

type DeleteSubjectProps = {
	subjectId: string;
	subjectTitle: string;
	onDeleted: () => void;
};

export function DeleteSubject({ subjectId, subjectTitle, onDeleted }: DeleteSubjectProps) {
	const executeDelete = async () => {
		try {
			await educationService.hardDeleteSubject(subjectId);
			onDeleted()
		} catch (err) {
			console.error(err);
		}
	};

	return (
		/* ---- Hard Delete Dialog ---- */
		<Dialog>
			<DialogTrigger asChild>
				<Button
					variant="ghost"
					className="h-8 px-2 text-red-500/60 hover:text-red-400 hover:bg-red-500/10 cursor-pointer flex gap-1.5 font-bold text-[9px] uppercase transition-all"
				>
					<ShieldAlert className="h-3.5 w-3.5" /> Hard
				</Button>
			</DialogTrigger>
			<DialogContent className="bg-zinc-950 border border-zinc-800 text-white shadow-2xl rounded-2xl p-6 [&>button]:hidden">
				<DialogClose asChild>
					<button className="absolute right-4 top-4 z-50 p-1 text-zinc-400 hover:text-red-500 transition-colors cursor-pointer outline-none group">
						<X className="h-4 w-4" />
					</button>
				</DialogClose>
				<DialogHeader>
					<DialogTitle className="text-red-500 font-black flex items-center gap-2 uppercase tracking-tighter text-xl">
						<AlertTriangle className="h-5 w-5" /> Critical Action
					</DialogTitle>
				</DialogHeader>
				<div className="py-6 text-sm text-zinc-400 leading-relaxed">
					You are about to{" "}
					<span className="text-white font-bold underline decoration-red-500/50 underline-offset-4">
						permanently destroy
					</span>{" "}
					the subject{" "}
					<span className="text-white font-bold">
						{subjectTitle}
					</span>
					. This data cannot be recovered.
				</div>
				<div className="flex gap-3">
					<DialogClose asChild>
						<Button
							variant="ghost"
							className="flex-1 bg-zinc-900 border border-zinc-800 cursor-pointer hover:bg-zinc-800 transition-colors font-bold rounded-xl h-11"
						>
							Abort
						</Button>
					</DialogClose>
					<Button
						onClick={() => executeDelete()}
						className="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold cursor-pointer transition-all rounded-xl h-11"
					>
						Confirm Purge
					</Button>
				</div>
			</DialogContent>
		</Dialog>
	);
}
