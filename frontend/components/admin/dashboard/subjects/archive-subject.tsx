import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
	DialogClose,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

import { X, Archive, Info, Trash2, Loader2 } from "lucide-react";
import { useState } from "react";

import { educationService } from "@/services/subjects.service";

type ArchiveSubjectProps = {
	subjectId: string;
	subjectTitle: string;
	onArchived: () => void;
};

export function ArchiveSubject({ subjectId, subjectTitle, onArchived }: ArchiveSubjectProps) {
	const [open, setOpen] = useState(false);
	const [loading, setLoading] = useState(false);

	const executeArchive = async () => {
		setLoading(true);
		try {
			await educationService.deleteSubject(subjectId);
			onArchived();
		} catch (err) {
			console.error(err);
		} finally {
			setLoading(false);
			setOpen(false);
		}
	};
	return (
		/* ---- Soft Delete Dialog ---- */
		<Dialog open={open} onOpenChange={setOpen}>
			<DialogTrigger asChild>
				<Button
					variant="ghost"
					className="h-8 px-2 text-yellow-500/60 hover:text-yellow-400 hover:bg-yellow-500/10 cursor-pointer flex gap-1.5 font-bold text-[9px] uppercase transition-all"
				>
					<Trash2 className="h-3 w-3" /> Soft
				</Button>
			</DialogTrigger>
			<DialogContent className="bg-zinc-950 border border-zinc-800 text-white shadow-2xl rounded-2xl p-6 [&>button]:hidden">
				<DialogClose asChild>
					<button className="absolute right-4 top-4 z-50 p-1 text-zinc-400 hover:text-yellow-500 transition-colors cursor-pointer outline-none group">
						<X className="h-4 w-4" />
					</button>
				</DialogClose>
				<DialogHeader>
					<DialogTitle className="text-yellow-500 font-black flex items-center gap-2 uppercase tracking-tighter text-xl">
						<Archive className="h-5 w-5" /> Archive Subject
					</DialogTitle>
				</DialogHeader>
				<div className="py-6 space-y-3">
					<p className="text-sm text-zinc-400 leading-relaxed">
						Moving{" "}
						<span className="text-white font-bold">
							{subjectTitle}
						</span>{" "}
						to archives.
					</p>
					<div className="flex items-start gap-3 bg-yellow-500/5 border border-yellow-500/10 p-3 rounded-xl">
						<Info className="h-4 w-4 text-yellow-500 shrink-0 mt-0.5" />
						<p className="text-[10px] text-yellow-500/80 leading-snug">
							The record will be hidden from live results but can
							be restored later from the 'Deleted' tab.
						</p>
					</div>
				</div>
				<div className="flex gap-3">
					<DialogClose asChild>
						<Button
							variant="ghost"
							className="flex-1 bg-zinc-900 border border-zinc-800 cursor-pointer hover:bg-zinc-800 transition-colors font-bold rounded-xl h-11"
						>
							Cancel
						</Button>
					</DialogClose>
					<Button
						onClick={() => executeArchive()}
						className="flex-1 bg-yellow-600 hover:bg-yellow-500 text-white font-bold cursor-pointer transition-all rounded-xl h-11"
						disabled={loading}
					>
						{loading ? (
							<Loader2 className="animate-spin h-4 w-4" />
						) : (
							"Archive Subject"
						)}
					</Button>
				</div>
			</DialogContent>
		</Dialog>
	);
}
