import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
	DialogClose,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useState } from "react";

import { Loader2, Zap, X, Activity, Power, Pencil } from "lucide-react";

import { educationService } from "@/services/subjects.service";

import type { SubmitEvent } from "react";
import type { Subject } from "./types";
import { Textarea } from "@/components/ui/textarea";

type EditSubjectProps = {
	subject: Subject;
	onEdit: (updated: Subject) => void;
};

export function EditSubject({ subject, onEdit }: EditSubjectProps) {
	const [loading, setLoading] = useState(false);
	const [active, setActive] = useState(subject.is_active);
	const [open, setOpen] = useState(false);

	const handleUpdate = async (e: SubmitEvent<HTMLFormElement>) => {
		e.preventDefault();

		setLoading(true);
		const formData = new FormData(e.currentTarget);

		const payload = {
			title: formData.get("title") as string,
			code: formData.get("code") as string,
			description: formData.get("description") as string,
			is_active: active,
		};

		try {
			const updated = await educationService.updateSubject(
				subject.id,
				payload,
			);
			onEdit(updated);
		} catch (err) {
			console.error(err);
		} finally {
			setLoading(false);
			setOpen(false);
		}
	};

	return (
		/* ---- Edit Subject Dialog ---- */
		<Dialog
			open={open}
			onOpenChange={setOpen}
		>
			<DialogTrigger asChild>
				<Button
					variant="ghost"
					className="h-8 px-2 text-blue-500/60 hover:text-blue-400 hover:bg-blue-500/10 cursor-pointer flex gap-1.5 font-bold text-[9px] uppercase transition-all"
				>
					<Pencil className="h-3 w-3" /> Edit
				</Button>
			</DialogTrigger>

			<DialogContent className="bg-zinc-950/85 backdrop-blur-xl border border-zinc-800 text-white sm:max-w-125 overflow-hidden rounded-2xl p-0 [&>button]:hidden shadow-2xl">
				<DialogClose asChild>
					<button className="absolute right-4 top-4 z-50 p-1 text-zinc-500 hover:text-red-500 transition-colors cursor-pointer outline-none group">
						<X className="h-5 w-5 group-hover:scale-110 transition-transform" />
					</button>
				</DialogClose>

				<div className="absolute inset-0 bg-linear-to-b from-blue-600/10 to-transparent pointer-events-none h-32" />

				<DialogHeader className="px-8 pt-8 pb-4 relative z-10">
					<div className="flex items-center gap-3 mb-1">
						<div className="p-2 rounded-lg bg-blue-600/10 border border-blue-500/20">
							<Pencil className="h-5 w-5 text-blue-500" />
						</div>
						<div>
							<DialogTitle className="text-2xl font-black tracking-tight uppercase">
								Edit Subject
							</DialogTitle>
							<p className="text-xs text-zinc-500 font-medium">
								Update the properties of this educational
								subject
							</p>
						</div>
					</div>
				</DialogHeader>

				<form
					onSubmit={handleUpdate}
					className="px-8 pb-8 space-y-6 relative z-10"
				>
					<div className="grid grid-cols-2 gap-4">
						<div className="col-span-2 md:col-span-1 space-y-2">
							<Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-2">
								<Activity className="h-3 w-3" /> Subject Title
							</Label>
							<Input
								name="title"
								defaultValue={subject?.title}
								placeholder="e.g. Mathematics"
								className="bg-zinc-900/30 border-zinc-800 h-11 focus:ring-2 focus:ring-blue-600/40 rounded-xl transition-all cursor-text"
								required
							/>
						</div>

						<div className="col-span-2 md:col-span-1 space-y-2">
							<Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-2">
								<Zap className="h-3 w-3" /> Module Code
							</Label>
							<Input
								name="code"
								defaultValue={subject?.code}
								placeholder="MATH-101"
								className="bg-zinc-900/30 border-zinc-800 h-11 focus:ring-2 focus:ring-blue-600/40 rounded-xl transition-all font-mono cursor-text"
								required
							/>
						</div>
					</div>

					<div className="space-y-2">
						<Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider">
							Detailed Description
						</Label>
						<Textarea
							name="description"
							defaultValue={subject?.description}
							placeholder="Briefly describe the curriculum..."
							className="bg-zinc-900/30 border-zinc-800 min-h-25 focus:ring-2 focus:ring-blue-600/40 rounded-xl transition-all resize-none cursor-text"
						/>
					</div>

					<div className="flex items-center justify-between rounded-2xl bg-blue-600/5 p-4 border border-zinc-800 group transition-all hover:bg-blue-600/10">
						<div className="flex gap-3 items-center">
							<div
								className={`p-2 rounded-lg transition-colors ${active ? "bg-blue-600 text-white" : "bg-zinc-800 text-zinc-500"}`}
							>
								<Power className="h-4 w-4" />
							</div>
							<div className="space-y-0.5">
								<Label className="text-sm font-bold block">
									Status: {active ? "Active" : "Inactive"}
								</Label>
								<p className="text-[10px] text-zinc-500">
									Toggle visibility of this subject
								</p>
							</div>
						</div>
						<Switch
							checked={active}
							onCheckedChange={setActive}
							className="data-[state=checked]:bg-blue-600 data-[state=unchecked]:bg-zinc-800 border-zinc-700 cursor-pointer"
						/>
					</div>

					<div className="flex gap-3 pt-2">
						<DialogClose asChild>
							<Button
								type="button"
								variant="ghost"
								className="flex-1 h-12 bg-zinc-900/50 hover:bg-red-600/20 hover:text-red-500 rounded-xl transition-all font-bold border border-zinc-800 cursor-pointer"
							>
								Cancel
							</Button>
						</DialogClose>
						<Button
							type="submit"
							disabled={loading}
							className="flex-2 h-12 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-lg shadow-blue-600/20 active:scale-[0.98] transition-all cursor-pointer"
						>
							{loading ? (
								<div className="flex items-center gap-2">
									<Loader2 className="animate-spin h-4 w-4" />
									<span>Updating...</span>
								</div>
							) : (
								"Update Subject"
							)}
						</Button>
					</div>
				</form>
			</DialogContent>
		</Dialog>
	);
}
