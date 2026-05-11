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
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Loader2, Zap, Plus, BookOpen, X, Activity, Power } from "lucide-react";
import { useState } from "react";

import { educationService } from "@/services/subjects.service";

import type { SubmitEvent } from "react";
import type { Subject } from "./types";

type AddSubjectProps = {
	onAdd: (subject: Subject) => void;
};

export function AddSubject({ onAdd }: AddSubjectProps) {
	const [open, setOpen] = useState(false);
	const [loading, setLoading] = useState(false);
	const [active, setActive] = useState(true);

	const handleCreate = async (e: SubmitEvent<HTMLFormElement>) => {
		e.preventDefault();
		setLoading(true);

        const form = e.currentTarget;
		const formData = new FormData(form);

		const payload = {
			title: formData.get("title") as string,
			code: formData.get("code") as string,
			description: formData.get("description") as string,
			is_active: active,
		};

		try {
			const res = await educationService.addSubject(payload);
			onAdd({ ...res, is_deleted: false });
			setOpen(false);
			setActive(true);
            form.reset();
		} catch (err) {
			console.error(err);
		} finally {
			setLoading(false);
		}
	};

	return (
		<Dialog
			open={open}
			onOpenChange={(val) => {
				setOpen(val);
				if (val) setActive(true);
			}}
		>
			<DialogTrigger asChild>
				<Button className="h-11 bg-blue-600 px-6 font-bold hover:bg-blue-500 rounded-xl cursor-pointer active:scale-95 transition-all shadow-lg shadow-blue-600/20">
					<Plus className="mr-2 h-4 w-4" /> Add Subject
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
							<BookOpen className="h-5 w-5 text-blue-500" />
						</div>
						<div>
							<DialogTitle className="text-2xl font-black tracking-tight uppercase">
								New Subject
							</DialogTitle>
							<p className="text-xs text-zinc-500 font-medium">
								Register a new educational subject in the system
							</p>
						</div>
					</div>
				</DialogHeader>

				<form
					onSubmit={handleCreate}
					className="px-8 pb-8 space-y-6 relative z-10"
				>
					<div className="grid grid-cols-2 gap-4">
						<div className="col-span-2 md:col-span-1 space-y-2">
							<Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-2">
								<Activity className="h-3 w-3" /> Subject Title
							</Label>
							<Input
								name="title"
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
									Initialize as Active
								</Label>
								<p className="text-[10px] text-zinc-500">
									Live subjects are immediately visible
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
								Discard
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
									<span>Deploying...</span>
								</div>
							) : (
								"Create Subject"
							)}
						</Button>
					</div>
				</form>
			</DialogContent>
		</Dialog>
	);
}
