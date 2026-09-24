; ModuleID = 'fib.ll'
source_filename = "fib.ll"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@__lumina_argc = local_unnamed_addr global i32 0
@__lumina_argv = local_unnamed_addr global ptr null
@str_0 = local_unnamed_addr constant [1 x i8] zeroinitializer
@str_1 = local_unnamed_addr constant [3 x i8] c"%s\00"
@str_2 = local_unnamed_addr constant [2 x i8] c" \00"
@str_3 = constant [4 x i8] c"%ld\00"
@str_4 = local_unnamed_addr constant [2 x i8] c"\0A\00"

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr nocapture noundef readonly, ...) local_unnamed_addr #0

declare void @GC_init() local_unnamed_addr

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i64 @strlen(ptr nocapture) local_unnamed_addr #1

declare i64 @atoi(ptr) local_unnamed_addr

; Function Attrs: nofree nosync nounwind memory(none)
define i64 @fib(i64 %.1) local_unnamed_addr #2 {
fib_entry:
  %icmp4 = icmp slt i64 %.1, 2
  br i1 %icmp4, label %common.ret, label %if_end

common.ret:                                       ; preds = %if_end, %fib_entry
  %accumulator.tr.lcssa = phi i64 [ 0, %fib_entry ], [ %add, %if_end ]
  %.1.tr.lcssa = phi i64 [ %.1, %fib_entry ], [ %sub.1, %if_end ]
  %accumulator.ret.tr = add i64 %.1.tr.lcssa, %accumulator.tr.lcssa
  ret i64 %accumulator.ret.tr

if_end:                                           ; preds = %fib_entry, %if_end
  %.1.tr6 = phi i64 [ %sub.1, %if_end ], [ %.1, %fib_entry ]
  %accumulator.tr5 = phi i64 [ %add, %if_end ], [ 0, %fib_entry ]
  %sub = add nsw i64 %.1.tr6, -1
  %fib_call = tail call i64 @fib(i64 %sub)
  %sub.1 = add nsw i64 %.1.tr6, -2
  %add = add i64 %fib_call, %accumulator.tr5
  %icmp = icmp ult i64 %.1.tr6, 4
  br i1 %icmp, label %common.ret, label %if_end
}

define noundef i32 @main(i32 %.1, ptr %.2) local_unnamed_addr {
main_entry:
  tail call void @GC_init()
  store i32 %.1, ptr @__lumina_argc, align 4
  store ptr %.2, ptr @__lumina_argv, align 8
  %argv_elem_ptr = getelementptr ptr, ptr %.2, i64 1
  %argv_elem = load ptr, ptr %argv_elem_ptr, align 8
  %len_str = tail call i64 @strlen(ptr noundef nonnull dereferenceable(1) %argv_elem)
  %icmp = icmp sgt i64 %len_str, 0
  br i1 %icmp, label %if_then, label %if_end

if_then:                                          ; preds = %main_entry
  %atoi_call = tail call i64 @atoi(ptr %argv_elem)
  br label %if_end

if_end:                                           ; preds = %main_entry, %if_then
  %n.0 = phi i64 [ %atoi_call, %if_then ], [ 35, %main_entry ]
  %fib_call = tail call i64 @fib(i64 %n.0)
  %putchar = tail call i32 @putchar(i32 32)
  %print_call.1 = tail call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) @str_3, i64 %fib_call)
  %putchar1 = tail call i32 @putchar(i32 10)
  ret i32 0
}

; Function Attrs: nofree nounwind
declare noundef i32 @putchar(i32 noundef) local_unnamed_addr #0

attributes #0 = { nofree nounwind }
attributes #1 = { mustprogress nofree nounwind willreturn memory(argmem: read) }
attributes #2 = { nofree nosync nounwind memory(none) }
